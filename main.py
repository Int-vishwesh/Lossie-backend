from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from matcher import save_item, find_best_matches
from fastapi import FastAPI, HTTPException, UploadFile, File
from db import db, upload_image

app = FastAPI(title="Lossie API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Next.js app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- frontend recieving format ---
class ItemRequest(BaseModel):
    title: str
    description: str
    category: str 

@app.get("/")
def read_root():
    return {"message": "Namaste! Lossie backend is live, type /docs to see the API"}

# Upload Endpoint
@app.post("/add-item")
async def add_new_item(
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    user_id: str = Form(...),
    file: UploadFile = File(None) 
):
    try:
        file_bytes = None
        filename = None
        content_type = None

        if file:
            allowed_types = ["image/jpeg", "image/png", "image/webp"]
            if file.content_type not in allowed_types:
                raise HTTPException(status_code=400, detail="Invalid file type!")
            file_bytes = await file.read()
            filename = file.filename
            content_type = file.content_type

        save_item(title, description, category, user_id, file_bytes, filename, content_type)
        
        matches_response = find_best_matches(category, description, file_bytes)
        
        if matches_response and hasattr(matches_response, 'data') and len(matches_response.data) > 0:
            best_match = matches_response.data[0]
            
            # update the status!
            if best_match.get('similarity', 0) > 0.85:
                match_id = best_match['id']
                db.table("items").update({"status": "matched"}).eq("id", match_id).execute()
                db.table("items").update({"status": "matched"}).eq("title", title).eq("description", description).execute()

        return {"status": "Success", "message": "Item saved and auto-scanned!"}

    except HTTPException as e:
        raise e  
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# User Profile -> All items
@app.get("/my-items/{user_id}")
async def get_user_items(user_id: str):
    """
    Fetches only the items reported by the specific logged-in user.
    """
    try:
        response = db.table("items").select("*").eq("user_id", user_id).execute()
        
        return {
            "status": "Success", 
            "data": response.data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Matchmaker Endpoint
@app.post("/find-matches")
async def find_item_matches(
    category: str = Form(...),
    description: str = Form(...),
    file: UploadFile = File(None) # Image optional
):
    try:
        file_bytes = None
        if file:
            allowed_types = ["image/jpeg", "image/png", "image/webp"]
            if file.content_type not in allowed_types:
                raise HTTPException(status_code=400, detail="Invalid file type!")
            file_bytes = await file.read()

        response = find_best_matches(category, description, file_bytes)
        
        return {
            "status": "Success",
            "matches_found": len(response.data),
            "results": response.data
        }
        
    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Feed Search page endpoint
@app.post("/search-feed")
async def search_feed_images(
    category: str = Form(...),
    file: UploadFile = File(...) # Image is REQUIRED here
):
    try:
        allowed_types = ["image/jpeg", "image/png", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid file type!")
        
        file_bytes = await file.read()
        
        target_category = "found" if category.lower() == "lost" else "lost"
        
        response = find_best_matches(target_category, "", file_bytes)
        
        return {
            "status": "Success",
            "matches_found": len(response.data) if response and hasattr(response, 'data') else 0,
            "results": response.data if response and hasattr(response, 'data') else []
        }

    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Image Upload Endpoint
@app.post("/upload-image")
async def handle_image_upload(file: UploadFile = File(...)):
    
    # check the MIME type.
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type: {file.content_type}. Only JPG, PNG, and WEBP allowed!"
        )

    try:
        # Reading raw pixels
        file_bytes = await file.read()
        image_url = upload_image(
            file_bytes=file_bytes,
            original_filename=file.filename,
            content_type=file.content_type
        )
        
        return {
            "status": "Success", 
            "message": "Image saved to Cloud!",
            "image_url": image_url
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# showing item in frontend
@app.get("/items")
async def get_all_items():
    try:
        # status
        response = db.table("items").select("id, title, description, category, image_url, status").execute()
        return {"status": "Success", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# item detail page endpoint
@app.get("/item/{item_id}")
async def get_single_item(item_id: str):
    try:
        response = db.table("items").select("*").eq("id", item_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Item not found")
            
        return {"status": "Success", "data": response.data[0]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
