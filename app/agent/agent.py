from app.llm.gemini_client import GeminiClient
from app.agent.prompts import SYSTEM_PROMPT


class SupportAgent:

    def __init__(self):
        self.llm = GeminiClient()

    def answer(
        self,
        user_message: str,
        context: str,
    ) -> str:

        prompt = f"""
Retrieved knowledge-base context:

--- BEGIN CONTEXT ---
{context}
--- END CONTEXT ---

Customer message:

{user_message}
"""

        return self.llm.generate(
            system_instruction=SYSTEM_PROMPT,
            user_message=prompt,
        )