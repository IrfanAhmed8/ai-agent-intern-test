import re


def format_response(response: str) -> str:
    """
    Cleans Gemini's response and moves source citations
    into a readable Sources section at the end.
    """

    sources = []

    # Match:
    # (`filename.md`, heading: *Heading*)
    pattern = re.compile(
        r"\(`([^`]+)`\s*,\s*heading:\s*\*([^*]+)\*\)"
    )

    def replace_source(match):
        filename = match.group(1)
        heading = match.group(2)

        source = (filename, heading)

        if source not in sources:
            sources.append(source)

        return ""

    # Remove source citations from the response.
    formatted = pattern.sub(replace_source, response)

    # Also handle citations using square brackets:
    # [`filename.md`, heading: *Heading*]
    bracket_pattern = re.compile(
        r"\[`([^`]+)`\s*,\s*heading:\s*\*([^*]+)\*\]"
    )

    def replace_bracket_source(match):
        filename = match.group(1)
        heading = match.group(2)

        source = (filename, heading)

        if source not in sources:
            sources.append(source)

        return ""

    formatted = bracket_pattern.sub(
        replace_bracket_source,
        formatted,
    )

    # Clean up whitespace left behind by removing citations.
    formatted = re.sub(
        r"[ \t]+\n",
        "\n",
        formatted,
    )

    formatted = re.sub(
        r"\n{3,}",
        "\n\n",
        formatted,
    )

    formatted = formatted.strip()

    # Add sources at the end.
    if sources:
        formatted += "\n\n**Sources:**\n"

        for filename, heading in sources:
            formatted += f"- `{filename}` — {heading}\n"

    return formatted.strip()