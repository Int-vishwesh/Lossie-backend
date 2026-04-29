from fastapi import FastAPI, HTTPException, UploadFile, File, Form
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
async def add_new_item(
    # We use Form(...) to tell FastAPI these are standard form fields, not JSON
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    # makes the photo optional
    file: UploadFile = File(None) 
):
    try:
        file_bytes = None
        filename = None
        content_type = None

        # If the user uploaded, read the bytes
        if file:
            allowed_types = ["image/jpeg", "image/png", "image/webp"]
            if file.content_type not in allowed_types:
                raise HTTPException(status_code=400, detail="Invalid file type!")
            
            file_bytes = await file.read()
            filename = file.filename
            content_type = file.content_type

        save_item(title, description, category, file_bytes, filename, content_type)
        
        return {"status": "Success", "message": "Multi-modal item saved!"}

    # Let intentional 400 errors pass through cleanly!
    except HTTPException as e:
        raise e 
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