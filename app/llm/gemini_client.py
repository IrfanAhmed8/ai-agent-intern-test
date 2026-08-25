from google import genai
from google.genai import types
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

    def generate_with_order_tool(
        self,
        system_instruction: str,
        user_message: str,
        order_lookup,
    ) -> str:

        order_tool = types.FunctionDeclaration(
            name="order_lookup",
            description=(
                "Look up a specific customer order by order ID. "
                "Use this when the customer asks about an order's "
                "status, shipping, tracking, or delivery."
            ),
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": (
                            "The exact order ID provided by the customer, "
                            "for example ORD-1007."
                        ),
                    }
                },
                "required": ["order_id"],
            },
        )

        tool = types.Tool(
            function_declarations=[order_tool]
        )

        response = self.client.models.generate_content(
            model=GENERATION_MODEL,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.0,
                tools=[tool],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
            ),
        )

        # Did Gemini request a tool call?
        if not response.function_calls:
            return response.text

        function_call = response.function_calls[0]

        if function_call.name != "order_lookup":
            raise ValueError(
                f"Unexpected tool call: {function_call.name}"
            )

        args = function_call.args
        order_id = args.get("order_id")

        if not order_id:
            raise ValueError(
                "order_lookup was called without order_id"
            )

        # ---------------------------------------------------------
        # DEBUG: TOOL CALL
        # ---------------------------------------------------------
        print("\n========== TOOL CALL ==========")
        print(f"Tool: {function_call.name}")
        print(f"Arguments: {{'order_id': '{order_id}'}}")
        print("================================\n")

        # Execute our deterministic Python tool.
        tool_result = order_lookup.lookup(order_id)

        # ---------------------------------------------------------
        # DEBUG: SANITIZED TOOL RESULT
        # ---------------------------------------------------------
        sanitized_result = {
            "found": tool_result.get("found"),
            "order_id": tool_result.get("order_id"),
            "status": tool_result.get("status"),
            "status_updated_at": tool_result.get("status_updated_at"),
            "customer_safe_message": tool_result.get(
                "customer_safe_message"
            ),
            "carrier": tool_result.get("carrier"),
            "estimated_delivery": tool_result.get(
                "estimated_delivery"
            ),
            "delivery_note": tool_result.get("delivery_note"),
            "handoff_required": tool_result.get(
                "handoff_required"
            ),
            "handoff_reason": tool_result.get(
                "handoff_reason"
            ),
        }

        # Remove fields that were not present in the actual result.
        sanitized_result = {
            key: value
            for key, value in sanitized_result.items()
            if value is not None
        }

        print("\n====== SANITIZED TOOL RESULT ======")
        print(f"Tool: order_lookup")
        print(f"Result: {sanitized_result}")
        print("===================================\n")

        # Send the function result back to Gemini.
        function_response_part = types.Part.from_function_response(
            name="order_lookup",
            response={
                "result": tool_result
            },
        )

        function_response_content = types.Content(
            role="user",
            parts=[function_response_part],
        )

        # Preserve the original user message + model tool-call response
        # + tool result for the final generation.
        response = self.client.models.generate_content(
            model=GENERATION_MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(
                            text=user_message
                        )
                    ],
                ),
                response.candidates[0].content,
                function_response_content,
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.0,
                tools=[tool],
            ),
        )

        return response.text