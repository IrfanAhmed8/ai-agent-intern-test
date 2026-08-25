from app.llm.gemini_client import GeminiClient
from app.tools.order_lookup import OrderLookup
from app.agent.prompts import SYSTEM_PROMPT


def test_order_tool_flow():

    client = GeminiClient()
    orders = OrderLookup()

    answer = client.generate_with_order_tool(
        system_instruction=SYSTEM_PROMPT,
        user_message="Where is ORD-1007 and when should it arrive?",
        order_lookup=orders,
    )

    print("\nANSWER:")
    print(answer)

    assert answer