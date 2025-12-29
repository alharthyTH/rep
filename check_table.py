import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

try:
    # Check if 'clients' table exists and has data
    res = supabase.table("clients").select("count", count="exact").execute()
    print(f"Total clients in DB: {res.count}")
except Exception as e:
    print(f"Error checking clients table: {e}")
