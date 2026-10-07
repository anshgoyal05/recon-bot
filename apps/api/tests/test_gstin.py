import pytest
from app.engine.gstin import validate_gstin, compute_gstin_checksum, get_state_code_from_gstin

def test_gstin_checksum_calculation():
    # Valid 14 character prefix for Tata AutoComp
    prefix = "27AAACT1234F1Z"
    expected_check = compute_gstin_checksum(prefix)
    assert expected_check == "R"

def test_valid_gstin():
    valid_gstin = "27AAACT1234F1ZR"
    is_valid, msg = validate_gstin(valid_gstin)
    assert is_valid is True
    assert msg == "Valid GSTIN"

def test_invalid_length():
    is_valid, msg = validate_gstin("27AAACT1234")
    assert is_valid is False
    assert "length" in msg.lower()

def test_invalid_state_code():
    # State code 99 is invalid
    is_valid, msg = validate_gstin("99AAACT1234F1Z8")
    assert is_valid is False
    assert "state code" in msg.lower()

def test_invalid_checksum():
    # Last char changed from 8 to 9
    is_valid, msg = validate_gstin("27AAACT1234F1Z9")
    assert is_valid is False
    assert "checksum" in msg.lower()

def test_get_state_code():
    assert get_state_code_from_gstin("27AAACT1234F1Z8") == "27"
    assert get_state_code_from_gstin("33AAACS1234D1Z2") == "33"
