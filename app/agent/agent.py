
import re

from app.llm.gemini_client import GeminiClient
from app.agent.prompts import SYSTEM_PROMPT
from app.retrieval.retriever import Retriever
from app.retrieval.context import format_context, select_context
from app.tools.order_lookup import OrderLookup
from app.llm.format_response import format_response
from app.history.chat_history import get_last_history, save_history
from app.history.context import format_history


ORDER_ID_PATTERN = re.compile(r"\bORD-\d+\b", re.IGNORECASE)


class SupportAgent:

    def __init__(self):
        self.llm = GeminiClient()
        self.retriever = Retriever()
        self.orders = OrderLookup()

    def answer(self, user_message: str) -> str:

        # ---------------------------------------------------------
        # 1. Get previous conversation history
        # ---------------------------------------------------------
        print("User Message")
        print(user_message)
        history = get_last_history(limit=5)
        print("\n========== HISTORY SELECTED ==========")

        for i, item in enumerate(history, start=1):
            print(f"\nHistory {i}")
            print(f"Query: {item['query']}")
            print(f"Response: {item['response']}")

        print("=======================================\n")

        history_context = format_history(history)

        # ---------------------------------------------------------
        # 2. Order questions
        # ---------------------------------------------------------

        if ORDER_ID_PATTERN.search(user_message):
            print("Detected order ID in user message. Using order lookup tool.")
            answer = self.llm.generate_with_order_tool(
                system_instruction=SYSTEM_PROMPT,
                user_message=f"""
Previous conversation history:

--- BEGIN HISTORY ---
{history_context}
--- END HISTORY ---

Current customer message:

{user_message}
""",
                order_lookup=self.orders,
            )

            # Save current conversation AFTER generating response
            save_history(
                query=user_message,
                response=answer,
            )

            return answer

        # ---------------------------------------------------------
        # 3. Normal RAG questions
        # ---------------------------------------------------------

        results = self.retriever.search(
            user_message,
            k=5,
            retrieve_k=10,
        )
        print("\n========== RETRIEVED CONTEXT ==========")

        for i, item in enumerate(results, start=1):
            chunk = item["chunk"]
            metadata = chunk["metadata"]

            print(f"\nContext {i}")
            print(f"File: {metadata.get('source')}")
            print(f"Semantic Score: {item.get('semantic_score')}")
            print(f"Metadata Score: {item.get('metadata_score')}")
            print(f"Final Score: {item.get('final_score')}")
            print(f"Metadata: {metadata}")

        print("========================================\n")
        selected = select_context(
            results,
            max_chunks=5,
        )

        context = format_context(selected)

        # ---------------------------------------------------------
        # 4. Build prompt with BOTH history + RAG context
        # ---------------------------------------------------------

        prompt = f"""
Previous conversation history:

--- BEGIN HISTORY ---
{history_context}
--- END HISTORY ---


Retrieved knowledge-base context:

--- BEGIN CONTEXT ---
{context}
--- END CONTEXT ---


Current customer message:

{user_message}
"""

        print("\n========== PROMPT ==========")
        print(prompt)

        # ---------------------------------------------------------
        # 5. Generate response
        # ---------------------------------------------------------

        answer = self.llm.generate(
            system_instruction=SYSTEM_PROMPT,
            user_message=prompt,
        )
        

        # ---------------------------------------------------------
        # 6. Save current query + response
        # ---------------------------------------------------------

        save_history(
            query=user_message,
            response=answer,
        )
        answer = format_response(answer)
        print ("\n========== Response ==========")
        print (answer)

        return answer

