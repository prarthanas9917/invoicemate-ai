import json
from unittest.mock import Mock, patch

import pytest

from invoice_utils import extract_invoice_details


@patch("invoice_utils.requests.post")
def test_extract_invoice_details_returns_normalized_fields(mock_post):
    mock_response = Mock()
    mock_response.json.return_value = {
        "response": json.dumps(
            {
                "vendor": "Paper Co.",
                "date": "2026-10-10",
                "amount": "850.50",
                "category": "Office Supplies",
                "description": "Printer paper",
            }
        )
    }
    mock_post.return_value = mock_response

    result = extract_invoice_details("Paper Co. total INR 850.50")

    assert result == {
        "vendor": "Paper Co.",
        "date": "2026-10-10",
        "amount": 850.50,
        "category": "Office Supplies",
        "description": "Printer paper",
    }
    mock_post.assert_called_once()
    mock_response.raise_for_status.assert_called_once()


@patch("invoice_utils.requests.post")
def test_extract_invoice_details_replaces_unknown_category(mock_post):
    mock_response = Mock()
    mock_response.json.return_value = {
        "response": '{"vendor":"Shop","category":"Unlisted","amount":null}'
    }
    mock_post.return_value = mock_response

    result = extract_invoice_details("Shop receipt")

    assert result["category"] == "Other"
    assert result["amount"] is None


@pytest.mark.parametrize("amount", ["not a number", -1, float("inf")])
@patch("invoice_utils.requests.post")
def test_extract_invoice_details_rejects_invalid_amount(mock_post, amount):
    mock_response = Mock()
    mock_response.json.return_value = {
        "response": json.dumps({"amount": amount})
    }
    mock_post.return_value = mock_response

    with pytest.raises(ValueError, match="amount"):
        extract_invoice_details("Receipt")


def test_extract_invoice_details_rejects_empty_text():
    with pytest.raises(ValueError, match="does not contain"):
        extract_invoice_details("  ")
