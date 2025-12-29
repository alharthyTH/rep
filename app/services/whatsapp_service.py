from twilio.rest import Client
from app.core.config import settings

def send_whatsapp_message(to_number: str, body_text: str):
    """
    Sends a WhatsApp message using the Twilio API.
    to_number should be in E.164 format, e.g., '+1234567890'
    Twilio handles the 'whatsapp:' prefix if needed.
    """
    if not all([settings.twilio_account_sid, settings.twilio_auth_token, settings.twilio_whatsapp_number]):
        print("Warning: Twilio credentials not fully configured.")
        return None

    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    
    # Ensure number format for WhatsApp
    to_whatsapp = f"whatsapp:{to_number}" if not to_number.startswith("whatsapp:") else to_number
    from_whatsapp = f"whatsapp:{settings.twilio_whatsapp_number}"
    
    try:
        message = client.messages.create(
            body=body_text,
            from_=from_whatsapp,
            to=to_whatsapp
        )
        print(f"WhatsApp message sent: {message.sid}")
        return message.sid
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        return None
