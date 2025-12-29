import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

location_id = "accounts/111/locations/1234567890"

print(f"Checking for location_id: {location_id}")
res = supabase.table("clients").select("*").eq("google_location_id", location_id).execute()
print(f"Exact match result: {res.data}")

if not res.data:
    print("No exact match. Checking all clients...")
    res_all = supabase.table("clients").select("*").execute()
    for row in res_all.data:
        print(f"Row: {row['google_location_id']}")
        if location_id in row['google_location_id'] or row['google_location_id'] in location_id:
            print("Found potential partial match!")
