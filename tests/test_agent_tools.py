import pytest
from agents.tools import call_tool, TOOLS

def test_unknown_tool_raises():
    with pytest.raises(ValueError):
        call_tool("does_not_exist", {})

def test_get_risk_score_tool_shape():
    result = call_tool("get_risk_score", {
        "amount": 5000, "sender_balance_before": 5000, "sender_balance_after": 0, "hour_of_day": 3,
    })
    assert "risk_score" in result
    assert "label" in result

def test_all_tools_well_described():
    for tool in TOOLS:
        assert len(tool["description"]) > 10  # catches placeholder/empty descriptions
