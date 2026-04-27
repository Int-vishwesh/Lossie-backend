# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from matcher import save_item, find_best_matches # NEW: Import our custom manager!

app = FastAPI(title="Lossie API")

# --- RULES FOR THE FRONTEND ---
class ItemRequest(BaseModel):
    title: str
    description: str
    category: str 

@app.get("/")
def read_root():
    return {"message": "Namaste! Lossie Matchmaker is online and SUPER clean!"}

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