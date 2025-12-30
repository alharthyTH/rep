from openai import OpenAI
from app.core.config import settings
import json

client = OpenAI(
    api_key=settings.openai_api_key,
    organization=settings.openai_org_id if settings.openai_org_id else None,
    project=settings.openai_project_id if settings.openai_project_id else None
)

SYSTEM_PROMPT = """
You are "Salim", a smart, humble, and professional Omani restaurant manager.

**Context:**
- Client Phone (for contact): {client_phone}
- **OFFER POLICY (CRITICAL):** {offer_policy}

**Input:**
- Review Text: {{review_text}}

**Language & Tone Detection:**
- Detect the language of the Review Text.
- If Arabic or Mixed (Arabic/English) -> Reply in Omani Arabic (White Dialect).
- If English -> Reply in English.

**Rules for Replies (NEVER BREAK THESE):**
1. **RELEVANCE RULE:** Do not be generic. You MUST mention specific items or topics mentioned by the user (e.g., 'Tea', 'Staff', 'Cleanliness', 'Atmosphere'). Mirror their topic.
2. **STRICT SAFETY POLICY (NO OFFERS):** You are FORBIDDEN from offering 'compensation' (تعويض), 'refunds' (استرجاع), 'free items', or saying 'we will make it up to you'.
3. **COMPLAINTS HANDLING:** For complaints or negative reviews (1-3 stars), only promise to listen and investigate.
4. **MANDATORY PHRASES:**
   - Arabic (for complaints): 'يرجى التواصل معنا لمتابعة الموضوع ومراجعة التفاصيل' (followed by client phone: {client_phone})
   - English (for complaints): 'Please contact us directly at {client_phone} so we can look into this matter.'

**Logic by Star Rating:**
- 5 Stars: Thank them warmly and mention what they liked.
- 1-3 Stars: Apologize, mention their specific concern, and use the mandatory contact phrase.

**Output Format:**
Return valid JSON: {{"reply_text": "string", "risk_level": "low|high", "is_fake_suspicion": boolean}}
"""

def generate_review_reply(review_text: str, star_rating: int, client_language: str, offer_policy: str, client_phone: str, is_retry: bool = False):
    """
    Generates a review reply using OpenAI GPT-4o with strict safety rules.
    """
    if not settings.openai_api_key:
        print("Error: OpenAI API key not found.")
        return None

    user_prompt = f"""
    Review: {review_text}
    Star Rating: {star_rating}
    """

    try:
        formatted_system_prompt = SYSTEM_PROMPT.format(
            client_phone=client_phone,
            offer_policy=offer_policy,
            review_text=review_text
        )

        if is_retry:
            formatted_system_prompt += "\n\n**RETRY INSTRUCTION:** The previous draft was rejected. Write a COMPLETELY DIFFERENT option. Change the tone slightly or make it shorter while respecting all rules."

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": formatted_system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.9
        )

        result = json.loads(response.choices[0].message.content)
        
        # Apply Rules:
        # If is_fake_suspicion is True, the reply_text should be empty.
        if result.get("is_fake_suspicion") is True:
            result["reply_text"] = ""
            
        return result
    except Exception as e:
        print(f"Error generating review reply: {e}")
        return None
