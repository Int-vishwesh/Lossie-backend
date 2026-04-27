import os
from dotenv import load_dotenv
from fastapi import FastAPI
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase URL or Key in .env file!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Lossie API")

@app.get("/")
def read_root():
    return {"message": "Lossie Backend is running"}

@app.post("/test-db")
def test_database_connection():
    dummy_data = {
        "title": "Secure Milton Bottle",
        "description": "Testing with .env variables!",
        "category": "lost"
    }
    
    try:
        response = supabase.table("items").insert(dummy_data).execute()
        return {"status": "Success", "data_saved": response.data}
    except Exception as e:
        return {"status": "Failed", "error": str(e)}