
from typing import List, Dict


def format_history(history: List[Dict[str, str]]) -> str:
    if not history:
        return "No previous conversation history."

    formatted = []

    for index, item in enumerate(history, start=1):
        formatted.append(
            f"""
Conversation {index}

Customer:
{item["query"]}

Assistant:
{item["response"]}
"""
        )

    return "\n".join(formatted)

