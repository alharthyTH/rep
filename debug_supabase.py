import os
from supabase import create_client
from dotenv import load_dotenv
import json

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"Connecting to: {url}")
supabase = create_client(url, key)

try:
    # 1. Try to list todos or any common table if exist, but better use a postgrest meta quest if possible
    # Supabase doesn't have a direct "list tables" in the client, but we can try to query common meta tables 
    # or just try to hit 'clients' again with a different approach.
    
    print("\n--- Testing 'clients' table ---")
    res = supabase.table("clients").select("*").limit(1).execute()
    print(f"Direct select * limit 1: {res.data}")
    
    # 2. Try to get all tables via RPC or direct SQL if allowed (usually not for anon key)
    # But let's try a simple query to see if we can see ANY data in the public schema
    print("\n--- Testing table count ---")
    res_count = supabase.table("clients").select("count", count="exact").execute()
    print(f"Exact count: {res_count.count}")

    # 3. Check if there are other tables we might have missed
    # (Since we can't easily list tables with anon key without knowing names, 
    # let's try to see if 'pending_reviews' has data)
    print("\n--- Testing 'pending_reviews' table ---")
    try:
        res_pending = supabase.table("pending_reviews").select("*").limit(1).execute()
        print(f"Pending reviews data: {res_pending.data}")
    except Exception as e:
        print(f"Error checking pending_reviews: {e}")

except Exception as e:
    print(f"\nCRITICAL ERROR: {e}")
