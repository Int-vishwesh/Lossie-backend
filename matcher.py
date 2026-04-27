# matcher.py
from db import db
from ai import generate_embedding

def save_item(title: str, description: str, category: str):
    """Generates AI numbers and saves the item to the database."""
    vector = generate_embedding(description)
    
    db_data = {
        "title": title,
        "description": description,
        "category": category.lower(),
        "embedding": vector
    }
    
    return db.table("items").insert(db_data).execute()

def find_best_matches(description: str, category: str):
    """Generates AI numbers and searches Supabase for a 85%+ match."""
    vector = generate_embedding(description)
    target_search_category = "found" if category.lower() == "lost" else "lost"
    
    return db.rpc(
        "match_items", 
        {
            "query_embedding": vector,
            "match_threshold": 0.85, 
            "match_count": 5,        
            "search_category": target_search_category
        }
    ).execute()