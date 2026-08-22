from google import genai

from app.config import GEMINI_API_KEY, GENERATION_MODEL


class GeminiClient:
    def __init__(self):
        self.client = genai.Client(
            api_key=GEMINI_API_KEY
        )

    def generate(
        self,
        system_instruction: str,
        user_message: str,
    ) -> str:

        response = self.client.models.generate_content(
            model=GENERATION_MODEL,
            contents=user_message,
            config={
                "system_instruction": system_instruction,
                "temperature": 0.0,
            },
        )

        return response.text