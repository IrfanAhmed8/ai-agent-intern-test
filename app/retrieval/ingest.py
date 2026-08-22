from pathlib import Path
import re
import yaml

from app.models import DocumentChunk, DocumentMetadata


FRONT_MATTER_PATTERN = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n(.*)$",
    re.DOTALL,
)


def parse_markdown_file(path: Path) -> tuple[DocumentMetadata, str]:
    """Parse YAML front matter and return metadata + markdown body."""

    content = path.read_text(encoding="utf-8")

    match = FRONT_MATTER_PATTERN.match(content)

    if not match:
        raise ValueError(f"Missing front matter: {path}")

    front_matter_text = match.group(1)
    body = match.group(2)

    metadata_dict = yaml.safe_load(front_matter_text)

    metadata = DocumentMetadata(**metadata_dict)

    return metadata, body


def split_by_headings(body: str) -> list[tuple[str | None, str]]:
    """
    Split markdown into logical sections based on ## headings.

    # Title is not treated as a section heading.
    ## headings start new chunks.
    """

    lines = body.splitlines()

    sections: list[tuple[str | None, list[str]]] = []

    current_heading: str | None = None
    current_content: list[str] = []

    for line in lines:
        if line.startswith("## "):
            if current_content:
                sections.append(
                    (current_heading, current_content)
                )

            current_heading = line[3:].strip()
            current_content = []
        else:
            current_content.append(line)

    if current_content:
        sections.append(
            (current_heading, current_content)
        )

    result = []

    for heading, content_lines in sections:
        content = "\n".join(content_lines).strip()

        if content:
            result.append((heading, content))

    return result


def build_chunks(path: Path) -> list[DocumentChunk]:
    """Parse one markdown document into heading-aware chunks."""

    metadata, body = parse_markdown_file(path)

    sections = split_by_headings(body)

    chunks = []

    for index, (heading, content) in enumerate(sections):
        heading_context = ""

        if heading:
            heading_context = f"Section: {heading}\n\n"

        text = (
            f"Document: {metadata.title}\n"
            f"{heading_context}"
            f"{content}"
        )

        chunk = DocumentChunk(
            chunk_id=f"{metadata.document_id}-{index}",
            text=text,
            source_file=path.name,
            document_id=metadata.document_id,
            title=metadata.title,
            heading=heading,
            metadata=metadata,
        )

        chunks.append(chunk)

    return chunks


def load_knowledge_base(directory: str | Path) -> list[DocumentChunk]:
    """Load all markdown files in the knowledge base."""

    directory = Path(directory)

    all_chunks = []

    for path in sorted(directory.glob("*.md")):
        chunks = build_chunks(path)
        all_chunks.extend(chunks)

    return all_chunks