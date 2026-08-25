from collections import defaultdict


def select_context(
    results: list[dict],
    max_chunks: int = 6,
    max_chunks_per_source: int = 2,
) -> list[dict]:
    """
    Select diverse, high-quality evidence for the LLM.

    Prefer multiple authoritative sources over many
    duplicate chunks from the same document.
    """

    selected = []
    source_counts = defaultdict(int)

    for result in results:
        chunk = result["chunk"]
        source = chunk["source_file"]

        if source_counts[source] >= max_chunks_per_source:
            continue

        selected.append(result)
        source_counts[source] += 1

        if len(selected) >= max_chunks:
            break

    return selected


def format_context(results: list[dict]) -> str:
    """
    Convert selected retrieval results into explicit,
    metadata-rich context for the LLM.
    """

    sections = []

    for result in results:
        chunk = result["chunk"]

        metadata = chunk["metadata"]

        section = f"""
SOURCE
filename: {chunk["source_file"]}
heading: {chunk.get("heading") or "Document"}
status: {metadata["status"]}
audience: {metadata["audience"]}
policy_authority: {metadata["policy_authority"]}

CONTENT:
{chunk["text"]}
"""

        sections.append(section.strip())

    return "\n\n---\n\n".join(sections)