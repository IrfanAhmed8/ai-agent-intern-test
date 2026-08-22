from pathlib import Path

from app.retrieval.ingest import (
    build_chunks,
    load_knowledge_base,
)


KB_DIR = Path("knowledge-base")


def test_current_returns_metadata_is_parsed():
    path = KB_DIR / "01-returns-policy-current.md"

    chunks = build_chunks(path)

    assert len(chunks) > 0

    chunk = chunks[0]

    assert chunk.document_id == "RET-2026-01"
    assert chunk.metadata.status == "active"
    assert chunk.metadata.audience == "customer"
    assert chunk.metadata.policy_authority == "official"


def test_standard_return_section_is_chunked():
    path = KB_DIR / "01-returns-policy-current.md"

    chunks = build_chunks(path)

    headings = [chunk.heading for chunk in chunks]

    assert "Standard return window" in headings


def test_legacy_policy_is_marked_superseded():
    path = KB_DIR / "02-returns-policy-legacy.md"

    chunks = build_chunks(path)

    assert len(chunks) > 0

    assert all(
        chunk.metadata.status == "superseded"
        for chunk in chunks
    )


def test_migration_scratchpad_is_not_customer_authority():
    path = KB_DIR / "14-internal-content-migration-notes.md"

    chunks = build_chunks(path)

    assert len(chunks) > 0

    for chunk in chunks:
        assert chunk.metadata.audience == "internal"
        assert chunk.metadata.policy_authority == "none"
        assert chunk.metadata.customer_answering is False


def test_load_entire_knowledge_base():
    chunks = load_knowledge_base(KB_DIR)

    assert len(chunks) > 0

    source_files = {
        chunk.source_file
        for chunk in chunks
    }

    assert "01-returns-policy-current.md" in source_files
    assert "06-international-shipping.md" in source_files
    assert "14-internal-content-migration-notes.md" in source_files

def test_chunk_contains_heading_context():
    path = KB_DIR / "01-returns-policy-current.md"

    chunks = build_chunks(path)

    standard_chunk = next(
        chunk
        for chunk in chunks
        if chunk.heading == "Standard return window"
    )

    assert "Returns Policy" in standard_chunk.text
    assert "Standard return window" in standard_chunk.text
    assert "30 calendar days" in standard_chunk.text


def test_chunk_preserves_source_file():
    path = KB_DIR / "01-returns-policy-current.md"

    chunks = build_chunks(path)

    assert all(
        chunk.source_file == "01-returns-policy-current.md"
        for chunk in chunks
    )


def test_chunks_have_unique_ids():
    chunks = load_knowledge_base(KB_DIR)

    ids = [chunk.chunk_id for chunk in chunks]

    assert len(ids) == len(set(ids))