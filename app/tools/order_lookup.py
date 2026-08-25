import json
import re
from pathlib import Path


ORDERS_FILE = Path("data/orders.json")


class OrderLookup:
    def __init__(self, orders_file: str | Path = ORDERS_FILE):
        self.orders_file = Path(orders_file)

        with self.orders_file.open("r", encoding="utf-8") as f:
            data = json.load(f)

        self.orders = {
            order["order_id"]: order
            for order in data["orders"]
        }

        self.snapshot_at = data["snapshot_at"]

    @staticmethod
    def normalize_order_id(order_id: str) -> str:
        """
        Normalize harmless formatting differences.

        Examples:
            'ord-1007'     -> 'ORD-1007'
            ' ORD-1007 '   -> 'ORD-1007'
            'ORD 1007'     -> 'ORD-1007'
        """
        normalized = order_id.strip().upper()

        # Only normalize ordinary punctuation/spacing.
        normalized = re.sub(r"[\s_]+", "-", normalized)

        return normalized

    def lookup(self, order_id: str) -> dict:
        """
        Look up an order and return only customer-safe information.
        """

        normalized_id = self.normalize_order_id(order_id)

        order = self.orders.get(normalized_id)

        if order is None:
            return {
                "found": False,
                "order_id": normalized_id,
                "message": (
                    "Order was not found. "
                    "Please check the order ID or contact support."
                ),
            }

        status = order["status"]

        result = {
            "found": True,
            "order_id": order["order_id"],
            "status": status,
            "status_updated_at": order["status_updated_at"],
            "customer_safe_message": order["customer_safe_message"],
        }

        # Only expose shipping/delivery information when appropriate.
        if status not in {"cancelled", "returned"}:
            result["carrier"] = order["carrier"]
            result["tracking_number"] = order["tracking_number"]
            result["estimated_delivery"] = order["estimated_delivery"]

        # Status-specific guidance for the agent.
        if status == "cancelled":
            result["delivery_note"] = (
                "The order is cancelled and will not be shipped."
            )

        elif status == "returned":
            result["delivery_note"] = (
                "The order has been returned and is not arriving."
            )

        elif status == "exception":
            result["handoff_required"] = True
            result["handoff_reason"] = (
                "The order has an operational exception and requires "
                "support review."
            )

        else:
            result["handoff_required"] = False

        return result