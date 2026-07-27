from app.embeddings.embedding_model import EmbeddingModel
from app.vectorstore.chroma_store import collection


class SemanticSearch:

    @staticmethod
    def search(query: str, top_k: int = 6):

        embedding_model = EmbeddingModel()

        query_embedding = embedding_model.embed(query)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        return results