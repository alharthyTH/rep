import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    # We allow this for now so the app can start even without env vars, 
    # but actual DB calls will fail.
    supabase: Client = None 
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
