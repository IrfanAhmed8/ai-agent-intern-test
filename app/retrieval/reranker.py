from typing import Any


class MetadataReranker:
    """
    Reranks semantically retrieved chunks using document metadata.

    Semantic similarity answers:
        "Is this content related to the question?"

    Metadata reranking answers:
        "Is this an appropriate source to use for a customer answer?"
    """

    def rerank(
        self,
        results: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        reranked = []

        for result in results:
            chunk = result["chunk"]
            metadata = chunk["metadata"]

            semantic_score = result["score"]

            metadata_score = self._metadata_score(metadata)

            final_score = (
                semantic_score
                + metadata_score
            )

            reranked.append(
                {
                    **result,
                    "semantic_score": semantic_score,
                    "metadata_score": metadata_score,
                    "final_score": final_score,
                }
            )

        reranked.sort(
            key=lambda x: x["final_score"],
            reverse=True,
        )

        return reranked

    def _metadata_score(self, metadata) -> float:
        score = 0.0

        # Current documents are preferred.
        if metadata["status"] == "active":
            score += 0.15

        # Superseded content should be strongly penalized.
        elif metadata["status"] == "superseded":
            score -= 0.20

        # Draft content should not become customer authority.
        elif metadata["status"] == "draft":
            score -= 0.15

        # Official company policy is preferred.
        if metadata["policy_authority"] == "official":
            score += 0.15

        elif metadata["policy_authority"] == "none":
            score -= 0.15

        # Customer-facing documents are preferred for
        # customer questions.
        if metadata["audience"] == "customer":
            score += 0.10

        elif metadata["audience"] == "internal":
            score -= 0.10

        # Some internal documents explicitly state whether
        # they can be used for customer answering.
        customer_answering = metadata.get(
            "customer_answering"
        )

        if customer_answering is True:
            score += 0.10

        elif customer_answering is False:
            score -= 0.20

        return score