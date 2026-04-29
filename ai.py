from sentence_transformers import SentenceTransformer
from PIL import Image # Vision library
import io

print("starting AI... please wait  ")
model = SentenceTransformer('clip-ViT-B-32')
print("AI is active!")

def generate_embedding(text: str) -> list[float]:
    """
    Takes a string of text and returns a 512-dimension vector.
    """
    # model.encode returns a numpy array converting it to list
    vector = model.encode(text).tolist()
    return vector

# ai vision
def generate_image_embedding(file_bytes: bytes) -> list[float]:
    """
    Takes raw image bytes, converts them into a picture, 
    and generates a 512-number vector from the visual data.
    """
    # digital bytes into actual Image 
    image = Image.open(io.BytesIO(file_bytes))
    
    # ai looking and doing math
    vector = model.encode(image).tolist()
    
    return vector