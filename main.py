from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from matcher import save_item, find_best_matches
from fastapi import FastAPI, HTTPException, UploadFile, File
from db import db, upload_image

app = FastAPI(title="Lossie API")

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
def add_new_item(item: ItemRequest):
    try:
        # We just hand the data to the manager!
        save_item(item.title, item.description, item.category)
        return {"status": "Success", "message": "Item and AI data saved!"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Matchmaker Endpoint
@app.post("/find-matches")
def find_item_matches(item: ItemRequest):
    try:
        # Hand it to the manager, get the results back!
        response = find_best_matches(item.description, item.category)
        
        return {
            "status": "Success",
            "matches_found": len(response.data),
            "results": response.data
        }
        
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
        
        # Pass to db.py function
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