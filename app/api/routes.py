from fastapi import APIRouter
from pydantic import BaseModel

from app.agent.agent import SupportAgent


router = APIRouter()
agent = SupportAgent()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer = agent.answer(request.message)

    return ChatResponse(answer=answer)