import os
import uuid # to generate unique file names
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase URL or Key in .env file!")

db: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Storing images
def upload_image(file_bytes: bytes, original_filename: str, content_type: str) -> str:
    """
    Uploads an image to the Supabase 'item-images' bucket and returns the public URL.
    """
    # 1. random ID for files
    unique_filename = f"{uuid.uuid4()}-{original_filename}"
    
    # 2. Upload the raw bytes to the bucket
    db.storage.from_("item-images").upload(
        path=unique_filename,
        file=file_bytes,
        file_options={"content-type": content_type}
    )
    
    # 3. Asking for public web address
    return db.storage.from_("item-images").get_public_url(unique_filename)