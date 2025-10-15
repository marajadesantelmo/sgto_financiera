import pandas as pd
import os
from datetime import datetime
from supabase import create_client, Client
import time

url_supabase = os.getenv("url_supabase")
key_supabase= os.getenv("key_supabase")

supabase_client = create_client(url_supabase, key_supabase)

def fetch_table_data(table_name, retries=3, delay=5):
    for attempt in range(retries):
        try:
            query = (
                supabase_client
                .from_(table_name)
                .select('*')
                .execute()
            )
            return pd.DataFrame(query.data)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise Exception(f"Failed to fetch data from {table_name} after {retries} attempts")

