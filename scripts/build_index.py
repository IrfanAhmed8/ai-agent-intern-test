from pathlib import Path

from app.retrieval.ingest import load_knowledge_base
from app.retrieval.embeddings import GeminiEmbedder
from app.retrieval.vector_store import VectorStore
from app.models import chunk_to_dict


KB_DIR = Path("knowledge-base")
ARTIFACTS_DIR = Path("artifacts")


def main():
    print("Loading knowledge base...")

    chunks = load_knowledge_base(KB_DIR)

    print(f"Loaded {len(chunks)} chunks.")

    embedder = GeminiEmbedder()

    texts = [
        chunk.text
        for chunk in chunks
    ]

    titles = [
        chunk.title
        for chunk in chunks
    ]

    print("Creating embeddings...")

    embeddings = embedder.embed_documents(
        texts=texts,
        titles=titles,
    )

    print(
        f"Created {len(embeddings)} embeddings."
    )
    

    serialized_chunks = [
        chunk_to_dict(chunk)
        for chunk in chunks
    ]
    assert len(chunks) == len(embeddings), (
        f"Chunk/embedding mismatch: "
        f"{len(chunks)} chunks, "
        f"{len(embeddings)} embeddings"
        )

    store = VectorStore(
        dimension=len(embeddings[0])
    )

    store.add(
        embeddings=embeddings,
        chunks=serialized_chunks,
    )

    store.save(ARTIFACTS_DIR)

    print(
        f"Saved FAISS index to {ARTIFACTS_DIR}"
    )


if __name__ == "__main__":
    main()