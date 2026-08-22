from datetime import date
from pydantic import BaseModel
from dataclasses import asdict

class DocumentMetadata(BaseModel):
    document_id: str
    title: str
    status: str
    effective_date: date
    last_reviewed: date
    audience: str
    policy_authority: str

    supersedes: str | None = None
    superseded_by: str | None = None
    customer_answering: bool | None = None


class DocumentChunk(BaseModel):
    chunk_id: str

    text: str

    source_file: str
    document_id: str
    title: str

    heading: str | None = None

    metadata: DocumentMetadata

def chunk_to_dict(chunk):
    return chunk.model_dump(mode="json")