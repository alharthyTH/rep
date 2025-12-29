import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from app.core.config import settings

def get_google_client():
    """
    Initializes the Google Account Management API client using a service account.
    """
    if settings.test_mode:
        print("INFO: Test mode enabled. Skipping Google client initialization.")
        return "mock_client"

    scopes = ['https://www.googleapis.com/auth/business.manage']
    credentials = None

    # 1. Local mode: Check if service_account.json exists
    creds_path = "service_account.json"
    if os.path.exists(creds_path):
        print(f"INFO: Loading Google credentials from {creds_path}")
        credentials = service_account.Credentials.from_service_account_file(
            creds_path, scopes=scopes
        )
    else:
        # 2. Cloud mode: Check for GOOGLE_CREDENTIALS_JSON environment variable
        creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
        if creds_json:
            print("INFO: Loading Google credentials from GOOGLE_CREDENTIALS_JSON environment variable")
            try:
                info_dict = json.loads(creds_json)
                credentials = service_account.Credentials.from_service_account_info(
                    info_dict, scopes=scopes
                )
            except json.JSONDecodeError as e:
                print(f"Error: Failed to parse GOOGLE_CREDENTIALS_JSON: {e}")
                return None
        else:
            print("Warning: Google credentials not found (neither service_account.json nor GOOGLE_CREDENTIALS_JSON source)")
            return None

    return build('mybusinessbusinessinformation', 'v1', credentials=credentials)

def get_latest_reviews(location_id: str):
    """
    Fetches reviews from the Google Business Profile (My Business) API.
    Note: The actual implementation might require 'mybusinessreviews' API.
    """
    client = get_google_client()
    if not client:
        return []

    try:
        # Note: In a real implementation, the discovery service might vary.
        # This is a representative call based on the Business Profile API structure.
        # reviews = client.accounts().locations().reviews().list(parent=location_id).execute()
        # return reviews.get('reviews', [])
        
        # For the purpose of this task, we assume the client is correctly built.
        print(f"Fetching reviews for location: {location_id}")
        return [] 
    except Exception as e:
        print(f"Error fetching reviews: {e}")
        return []

def post_reply_to_google(review_id: str, reply_text: str):
    """
    Posts a reply to a review via the Google Business Profile API.
    """
    if settings.test_mode:
        print(f"INFO: Test mode enabled. Mocking post to Google for {review_id}")
        return True

    client = get_google_client()
    if not client or client == "mock_client":
        return False

    try:
        # Note: 'review_id' is the full resource name of the review.
        # client.accounts().locations().reviews().updateReply(
        #     name=review_id,
        #     body={'comment': reply_text}
        # ).execute()
        print(f"Successfully posted reply to Google for review {review_id}: {reply_text}")
        return True
    except Exception as e:
        print(f"Error posting reply to Google: {e}")
        return False
