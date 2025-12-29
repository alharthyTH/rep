from fastapi import FastAPI, Request, Form, Response
import base64
import json
from app.db.supabase import supabase
from app.services.openai_service import generate_review_reply
from app.services.whatsapp_service import send_whatsapp_message
from app.services.google_client import post_reply_to_google

app = FastAPI(
    title="Review Management AI Backend",
    description="FastAPI backend for managing shop reviews and interactions.",
    version="0.1.0"
)

STAR_RATING_MAP = {
    "ONE": 1,
    "TWO": 2,
    "THREE": 3,
    "FOUR": 4,
    "FIVE": 5
}

def get_daily_stats(client_id: str):
    """
    Counts pending and posted reviews for today.
    """
    from datetime import datetime, date
    today = date.today().isoformat()
    
    # pending: Reviews with status 'pending' (formerly 'queued' or 'sent_for_approval' in prompt context)
    pending_res = supabase.table("pending_reviews") \
        .select("id", count="exact") \
        .eq("client_id", client_id) \
        .eq("status", "pending") \
        .execute()
    
    # posted: Reviews with status 'posted' updated today
    posted_res = supabase.table("pending_reviews") \
        .select("id", count="exact") \
        .eq("client_id", client_id) \
        .eq("status", "posted") \
        .gte("updated_at", today) \
        .execute()
    
    return {
        "pending": pending_res.count or 0,
        "posted": posted_res.count or 0
    }

async def approve_review(phone_number: str):
    """Posts the latest pending review to Google."""
    # Identify Client
    client_res = supabase.table("clients").select("id").eq("phone_number", phone_number).execute()
    if not client_res.data:
        return False
    
    client_id = client_res.data[0]["id"]

    # Get latest pending review
    pending_res = supabase.table("pending_reviews") \
        .select("*") \
        .eq("client_id", client_id) \
        .eq("status", "pending") \
        .order("created_at", desc=True) \
        .limit(1) \
        .execute()

    if not pending_res.data:
        return False

    pending_review = pending_res.data[0]
    success = post_reply_to_google(pending_review["google_review_id"], pending_review["draft_reply"])
    
    if success:
        supabase.table("pending_reviews").update({"status": "posted"}).eq("id", pending_review["id"]).execute()
        send_whatsapp_message(phone_number, "Review reply posted successfully!")
    else:
        send_whatsapp_message(phone_number, "Error posting reply to Google.")
    return success

async def regenerate_draft(phone_number: str):
    """Generates a new AI draft for the latest pending review."""
    client_res = supabase.table("clients").select("*").eq("phone_number", phone_number).execute()
    if not client_res.data:
        return False
    
    client = client_res.data[0]
    client_id = client["id"]

    pending_res = supabase.table("pending_reviews") \
        .select("*") \
        .eq("client_id", client_id) \
        .eq("status", "pending") \
        .order("created_at", desc=True) \
        .limit(1) \
        .execute()

    if not pending_res.data:
        return False

    pending_review = pending_res.data[0]
    ai_reply = generate_review_reply(
        pending_review["review_text"], 
        pending_review["star_rating"], 
        client["language_preference"], 
        client.get("offer_policy", ""), 
        is_retry=True
    )

    if ai_reply:
        new_draft = ai_reply.get("reply_text", "")
        supabase.table("pending_reviews").update({"draft_reply": new_draft}).eq("id", pending_review["id"]).execute()
        
        from datetime import datetime
        stats = get_daily_stats(client_id)
        current_date = datetime.now().strftime("%d %b")
        
        whatsapp_body = (
            f"📊 Dashboard • {current_date}\n"
            f"🔴 Pending: {stats['pending']} | ✅ Posted: {stats['posted']}\n\n"
            f"⭐ New {pending_review['star_rating']} Review\n"
            f"👤 Customer\n"
            f"\"{pending_review['review_text']}\"\n\n"
            f"🤖 Proposed Reply: \"{new_draft}\"\n\n"
            f"👇 Action: 1 : Approve 2 : 🎲 Regenerate"
        )
        send_whatsapp_message(phone_number, whatsapp_body)
        return True
    return False

async def post_batched_reviews(phone_number: str):
    """Posts ALL reviews with 'pending' status for the client."""
    client_res = supabase.table("clients").select("id").eq("phone_number", phone_number).execute()
    if not client_res.data:
        return False
    
    client_id = client_res.data[0]["id"]
    pending_res = supabase.table("pending_reviews") \
        .select("*") \
        .eq("client_id", client_id) \
        .eq("status", "pending") \
        .execute()

    if not pending_res.data:
        send_whatsapp_message(phone_number, "No pending reviews to post.")
        return False

    count = 0
    for review in pending_res.data:
        success = post_reply_to_google(review["google_review_id"], review["draft_reply"])
        if success:
            supabase.table("pending_reviews").update({"status": "posted"}).eq("id", review["id"]).execute()
            count += 1

    send_whatsapp_message(phone_number, f"Batch complete: {count} reviews posted!")
    return True

@app.get("/")
async def root():
    return {
        "message": "Review Management AI API is running",
        "supabase_connected": supabase is not None
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/webhook/google-pubsub")
async def google_pubsub_webhook(request: Request):
    """
    Receives notifications from Google Cloud Pub/Sub.
    """
    payload = await request.json()
    message = payload.get("message", {})
    data_b64 = message.get("data")
    
    if not data_b64:
        return {"status": "no data"}

    try:
        data_str = base64.b64decode(data_b64).decode("utf-8")
        # Use strict=False to handle control characters that might be present in the data
        data_json = json.loads(data_str, strict=False)
        
        # In a real scenario, we extract location_id and review_id from the notification
        # We try both standard notification keys and raw review object keys (often used in tests)
        location_id = data_json.get("locationName")
        review_id = data_json.get("reviewName") or data_json.get("name")
        review_text = data_json.get("reviewText") or data_json.get("comment", "No text provided")
        reviewer_name = data_json.get("reviewer", {}).get("displayName") or "Customer"
        
        # Google API can send ratings as strings (e.g., "ONE", "FIVE") or integers.
        raw_rating = data_json.get("starRating", 5)
        if isinstance(raw_rating, str):
            star_rating = STAR_RATING_MAP.get(raw_rating.upper(), 5)
        else:
            star_rating = int(raw_rating)

        # If locationName is missing but reviewName/name is present, extract location from it
        if not location_id and review_id and "/reviews/" in review_id:
            location_id = review_id.split("/reviews/")[0]

        if not location_id:
            print(f"DEBUG: Missing location_id. Extracted location_id: {location_id}, review_id: {review_id}")
            return {"status": "missing location_id"}

        # 1. Fetch Client from Supabase
        print(f"DEBUG: Querying clients table for google_location_id='{location_id}'")
        client_res = supabase.table("clients").select("*").eq("google_location_id", location_id).execute()
        
        print(f"DEBUG: Supabase query result: {client_res.data}")
        
        if not client_res.data:
            print(f"Client not found for location: {location_id}")
            return {"status": "client not found"}
        
        client = client_res.data[0]
        client_id = client["id"]
        client_phone = client["phone_number"]
        client_lang = client["language_preference"]
        offer_policy = client.get("offer_policy", "STRICT - NO OFFERS")

        # 2. Generate AI Draft
        ai_reply = generate_review_reply(review_text, star_rating, client_lang, offer_policy)
        if not ai_reply:
            return {"status": "AI generation failed"}

        draft_text = ai_reply.get("reply_text", "")
        
        # 3. Store in pending_reviews
        pending_data = {
            "client_id": client_id,
            "google_review_id": review_id,
            "review_text": review_text,
            "star_rating": star_rating,
            "draft_reply": draft_text,
            "status": "pending"
        }
        supabase.table("pending_reviews").insert(pending_data).execute()

        # 4. Send WhatsApp Notification
        from datetime import datetime
        stats = get_daily_stats(client_id)
        current_date = datetime.now().strftime("%d %b")
        
        # New format mockup: '📊 Dashboard • {date} 🔴 Pending: {pending} | ✅ Posted: {posted} ...'
        whatsapp_body = (
            f"📊 Dashboard • {current_date}\n"
            f"🔴 Pending: {stats['pending']} | ✅ Posted: {stats['posted']}\n\n"
            f"⭐ New {star_rating} Review\n"
            f"👤 {reviewer_name}\n"
            f"\"{review_text}\"\n\n"
            f"🤖 Proposed Reply: \"{draft_text}\"\n\n"
            f"👇 Action: 1 : Approve 2 : 🎲 Regenerate"
        )
        send_whatsapp_message(client_phone, whatsapp_body)

    except Exception as e:
        print(f"Error in Google webhook workflow: {e}")
    
    return {"status": "accepted"}

@app.post("/webhook/twilio")
async def twilio_webhook(From: str = Form(...), Body: str = Form(...)):
    """
    Receives user replies from Twilio (WhatsApp).
    """
    from_number = From.replace("whatsapp:", "")
    body = Body.strip()

    if body == "1":
        await approve_review(from_number)
    elif body == "2":
        await regenerate_draft(from_number)
    elif body.upper() == "ALL":
        await post_batched_reviews(from_number)
    
    # Return standard TwiML response
    return Response(content="<Response></Response>", media_type="text/xml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
