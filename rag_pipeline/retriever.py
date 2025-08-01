from sentence_transformers import SentenceTransformer, util
import torch

# Load sentence embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_top_chunks(chunks: list[str], question: str, top_k: int = 5):
    chunk_embeddings = model.encode(chunks, convert_to_tensor=True)
    question_embedding = model.encode(question, convert_to_tensor=True)

    # Cosine similarity
    cos_scores = util.cos_sim(question_embedding, chunk_embeddings)[0]
    top_results = torch.topk(cos_scores, k=top_k)

    return [chunks[idx] for idx in top_results.indices]
