from app.tools.order_lookup import OrderLookup


def test_valid_order_lookup():
    tool = OrderLookup()

    result = tool.lookup("ORD-1007")

    assert result["found"] is True
    assert result["order_id"] == "ORD-1007"
    assert result["status"] == "shipped"


def test_order_id_is_case_insensitive():
    tool = OrderLookup()

    result = tool.lookup("ord-1007")

    assert result["found"] is True
    assert result["order_id"] == "ORD-1007"


def test_order_id_strips_whitespace():
    tool = OrderLookup()

    result = tool.lookup("  ORD-1007  ")

    assert result["found"] is True
    assert result["order_id"] == "ORD-1007"


def test_unknown_order_is_safe():
    tool = OrderLookup()

    result = tool.lookup("ORD-9999")

    assert result["found"] is False
    assert "not found" in result["message"].lower()


def test_internal_fields_are_never_returned():
    tool = OrderLookup()

    result = tool.lookup("ORD-1007")

    result_text = str(result).lower()

    assert "email" not in result_text
    assert "shipping_address" not in result_text
    assert "risk_score" not in result_text
    assert "warehouse_note" not in result_text
    assert "support_tags" not in result_text


def test_cancelled_order_does_not_expose_stale_delivery_data():
    tool = OrderLookup()

    result = tool.lookup("ORD-1004")

    assert result["found"] is True
    assert result["status"] == "cancelled"

    assert "estimated_delivery" not in result
    assert "carrier" not in result
    assert "tracking_number" not in result

    assert "will not be shipped" in result["delivery_note"]


def test_shipped_order_without_eta_does_not_invent_one():
    tool = OrderLookup()

    result = tool.lookup("ORD-1011")

    assert result["found"] is True
    assert result["status"] == "shipped"
    assert result["estimated_delivery"] is None