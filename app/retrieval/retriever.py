from pathlib import Path

from app.retrieval.embeddings import GeminiEmbedder
from app.retrieval.vector_store import VectorStore
from app.retrieval.reranker import MetadataReranker
from app.retrieval.context import select_context

class Retriever:

    def __init__(
        self,
        artifacts_dir: str | Path = "artifacts",
    ):
        self.embedder = GeminiEmbedder()
        self.store = VectorStore.load(artifacts_dir)
        self.reranker = MetadataReranker()

    def search(
        self,
        query: str,
        k: int = 5,
        retrieve_k: int = 10,
    ):
        query_embedding = self.embedder.embed_query(query)

        # Retrieve more candidates than we finally return.
        candidates = self.store.search(
            query_embedding=query_embedding,
            k=retrieve_k,
        )
        print(f"Retrieved {len(candidates)} candidates from vector store.")

        # Apply deterministic metadata-aware reranking.
        reranked = self.reranker.rerank(
            candidates
        )
        return select_context(
            reranked,
            max_chunks=k,
        )