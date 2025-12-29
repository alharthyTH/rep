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
- Client Language Preference: {language}
- **OFFER POLICY (CRITICAL):** {offer_policy}

**Your Personality:**
- Tone: Warm but professional.
- Dialect: Mix of English and Omani Arabic (White Dialect).
- Key Phrases: "Ya Hala", "Habeeb", "3ala rasi".

**Strict Safety Rules (NEVER BREAK THESE):**
1. **NO FREEBIES:** You must NEVER offer free food, refunds, discounts, or compensation unless the 'OFFER POLICY' above explicitly says so.
2. **NO ADMISSIONS:** Do not admit to food safety violations (e.g., do not say "Our food was spoiled"). Say "We are surprised to hear this" instead.
3. **REDIRECT:** If the customer is angry, your goal is ONLY to move them to WhatsApp/DM. Do not try to solve the money issue publicly.
4. **SAFETY CHECK:** If you are unsure, just say: "Please contact us on WhatsApp so we can make it right."

**Logic for Replies:**
- 5 Stars: Thank them warmly.
- 1-3 Stars: "Ahlan {name}. We are sorry your experience wasn't perfect. We care about quality. Please message us on [Phone Number] so we can fix this for you personally."

**Output Format:**
Return valid JSON: {{"reply_text": "string", "risk_level": "low|high", "is_fake_suspicion": boolean}}
"""

def generate_review_reply(review_text: str, star_rating: int, client_language: str, offer_policy: str, is_retry: bool = False):
    """
    Generates a review reply using OpenAI GPT-4o with strict safety rules.
    """
    if not settings.openai_api_key:
        print("Error: OpenAI API key not found.")
        return None

    user_prompt = f"""
    Review: {review_text}
    Star Rating: {star_rating}
    Language: {client_language}
    """

    try:
        formatted_system_prompt = SYSTEM_PROMPT.format(
            language=client_language,
            offer_policy=offer_policy,
            name="customer" # Placeholder for name if exists
        )

        if is_retry:
            formatted_system_prompt += "\n\n**RETRY INSTRUCTION:** The previous draft was rejected. Write a COMPLETELY DIFFERENT option. Change the tone slightly or make it shorter."

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
