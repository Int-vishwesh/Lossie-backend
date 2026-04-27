from sentence_transformers import SentenceTransformer

print("starting AI... please wait  ")
model = SentenceTransformer('clip-ViT-B-32')
print("AI is active!")

def generate_embedding(text: str) -> list[float]:
    """
    Takes a string of text and returns a 512-dimension vector.
    """
    # model.encode returns a numpy array, so we convert it to a standard Python list
    vector = model.encode(text).tolist()
    return vector