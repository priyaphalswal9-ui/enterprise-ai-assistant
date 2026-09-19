from langchain_community.embeddings import HuggingFaceEmbeddings


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def generate_embedding(text: str) -> list[float]:
    return embeddings.embed_query(text)