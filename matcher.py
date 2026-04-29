from fastapi import HTTPException
from db import db, upload_image
from ai import generate_embedding, generate_image_embedding
import math

def calculate_similarity(vector1, vector2):
    """Calculates how closely two AI vectors match (Cosine Similarity) image to math within same user"""
    dot_product = sum(a * b for a, b in zip(vector1, vector2))
    magnitude1 = math.sqrt(sum(a * a for a in vector1))
    magnitude2 = math.sqrt(sum(b * b for b in vector2))
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    return dot_product / (magnitude1 * magnitude2)


def save_item(title: str, description: str, category: str, file_bytes: bytes = None, filename: str = None, content_type: str = None):
    
    # text math
    text_vector = generate_embedding(description)
    
    db_data = {
        "title": title,
        "description": description,
        "category": category.lower(),
        "text_embedding": text_vector
    }
    
    # 35% Bouncer
    if file_bytes and filename and content_type:
        image_vector = generate_image_embedding(file_bytes)
        
        # Consistency Bouncer
        consistency_score = calculate_similarity(text_vector, image_vector)
        print(f"Bouncer Score: {consistency_score}")
        
        if consistency_score < 0.25: # 25% min threshold
            # reject upload entirely
            raise HTTPException(
                status_code=400, 
                detail="Quality Alert: Your photo does not clearly match your description. Please upload a clearer photo or leave the image empty!"
            )

        # when passes the bouncer
        image_url = upload_image (file_bytes, filename, content_type)
        db_data["image_url"] = image_url
        db_data["image_embedding"] = image_vector
        
    return db.table("items").insert(db_data).execute()


def find_best_matches(category: str, description: str, file_bytes: bytes = None):
    """Calculates both Text and Image vectors and runs a 4-Way Match."""
    
    # Text mandatory
    search_text_vector = generate_embedding(description)
    
    # optional Image 
    if file_bytes:
        search_image_vector = generate_image_embedding(file_bytes)
    else:
        search_image_vector = None 

    target_search_category = "found" if category.lower() == "lost" else "lost"
    
    # Send BOTH
    return db.rpc(
        "match_items", 
        {
            "search_text_vector": search_text_vector,
            "search_image_vector": search_image_vector,
            "match_threshold": 0.85, # 85% min threshold
            "match_count": 5,        
            "search_category": target_search_category
        }
    ).execute()