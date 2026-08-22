from app.retrieval.embeddings import GeminiEmbedder


embedder = GeminiEmbedder()

result = embedder.embed_documents(
    texts=[
        "Customers on the standard plan may request a return within 30 calendar days of delivery."
    ],
    titles=[
        "Returns Policy"
    ],
)

print("Number of embeddings:", len(result))
print("Vector dimensions:", len(result[0]))