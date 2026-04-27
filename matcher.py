from db import db, upload_image
from ai import generate_embedding, generate_image_embedding

def save_item(title: str, description: str, category: str, file_bytes: bytes = None, filename: str = None, content_type: str = None):
    """Generates AI numbers for both text and images, then saves to Supabase."""
    
    # Text Math 
    text_vector = generate_embedding(description)
    
    db_data = {
        "title": title,
        "description": description,
        "category": category.lower(),
        "text_embedding": text_vector
    }
    
    # Image Math
    if file_bytes and filename and content_type:
        image_url = upload_image(file_bytes, filename, content_type)
        image_vector = generate_image_embedding(file_bytes)
        
        db_data["image_url"] = image_url
        db_data["image_embedding"] = image_vector
        
    return db.table("items").insert(db_data).execute()


def find_best_matches(category: str, description: str = None, file_bytes: bytes = None):
    """Generates a search vector (from image OR text) and finds the highest match."""
    
    # decide which vector to use. 
    if file_bytes:
        search_vector = generate_image_embedding(file_bytes)
    # if no photo use text description
    elif description:
        search_vector = generate_embedding(description)
    else:
        raise ValueError("You must provide either a description or an image to search!")

    # lost vs found
    target_search_category = "found" if category.lower() == "lost" else "lost"
    
    return db.rpc(
        "match_items", 
        {
            "search_vector": search_vector,
            "match_threshold": 0.85, 
            "match_count": 5,        
            "search_category": target_search_category
        }
    ).execute()