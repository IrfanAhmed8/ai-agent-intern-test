from google import genai
from google.genai import types
from app.config import GEMINI_API_KEY, EMBEDDING_MODEL


class GeminiEmbedder:
    def __init__(self):
        self.client = genai.Client(
            api_key=GEMINI_API_KEY
        )

    def embed_documents(
        self,
        texts: list[str],
        titles: list[str],
    ) -> list[list[float]]:
        """Create one embedding per knowledge-base chunk."""

        if len(texts) != len(titles):
            raise ValueError(
                "texts and titles must have the same length"
            )

        all_embeddings = []

        for i, (text, title) in enumerate(
            zip(texts, titles),
            start=1,
        ):
            input_text = (
                f"title: {title} | text: {text}"
            )

            response = self.client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=input_text,
                config=types.EmbedContentConfig(
                    output_dimensionality=768,
                ),
            )

            all_embeddings.append(
                response.embeddings[0].values
            )

            print(
                f"Embedded {i}/{len(texts)}"
            )

        return all_embeddings

    def embed_query(self, query: str) -> list[float]:
        """Create an embedding for a user's search query."""

        formatted_query = (
            f"task: question answering | query: {query}"
        )

        response = self.client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=formatted_query,
            config=types.EmbedContentConfig(
            output_dimensionality=768,
            ),
        )

        return response.embeddings[0].values