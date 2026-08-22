import json
from pathlib import Path

import faiss
import numpy as np


class VectorStore:
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.chunks = []

    def add(self, embeddings, chunks):
        vectors = np.asarray(
            embeddings,
            dtype="float32",
        )

        # Normalize because we'll use cosine similarity
        faiss.normalize_L2(vectors)

        self.index.add(vectors)
        self.chunks.extend(chunks)

    def search(self, query_embedding, k=5):
        query = np.asarray(
            [query_embedding],
            dtype="float32",
        )

        faiss.normalize_L2(query)

        scores, indices = self.index.search(query, k)

        results = []

        for score, index in zip(scores[0], indices[0]):
            if index == -1:
                continue

            results.append(
                {
                    "score": float(score),
                    "chunk": self.chunks[index],
                }
            )

        return results

    def save(self, directory):
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        faiss.write_index(
            self.index,
            str(directory / "index.faiss"),
        )

        with open(
            directory / "chunks.json",
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                self.chunks,
                f,
                indent=2,
                ensure_ascii=False,
            )

    @classmethod
    def load(cls, directory):
        directory = Path(directory)

        index = faiss.read_index(
            str(directory / "index.faiss")
        )

        with open(
            directory / "chunks.json",
            encoding="utf-8",
        ) as f:
            chunks = json.load(f)

        store = cls(index.d)
        store.index = index
        store.chunks = chunks

        return store