from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

def cosine_similarity_score(original: str, optimized: str) -> float:
    emb1 = model.encode(original, convert_to_tensor=True)
    emb2 = model.encode(optimized, convert_to_tensor=True)
    return float(util.cos_sim(emb1, emb2))