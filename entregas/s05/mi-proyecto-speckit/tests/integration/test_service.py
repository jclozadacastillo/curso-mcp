"""
Integration tests (in-memory, NO subprocess).
Validates interaction between TemperatureService and the core converter engine.
"""

import pytest
from src.temp_converter.service import TemperatureService


def test_service_successful_conversion_pipeline():
    service = TemperatureService("TestService")
    payload = service.execute_conversion(100, "C", "F")

    assert payload["service"] == "TestService"
    assert payload["input_value"] == 100.0
    assert payload["from_unit"] == "C"
    assert payload["to_unit"] == "F"
    assert payload["result"] == 212.00
    assert payload["formatted"] == "212.00 F"


def test_service_string_numeric_parsing():
    service = TemperatureService()
    payload = service.execute_conversion("32.0", "F", "C")
    assert payload["result"] == 0.00
    assert payload["formatted"] == "0.00 C"


def test_service_error_handling_propagation():
    service = TemperatureService()
    # Invalid string input
    with pytest.raises(TypeError, match="cannot be converted to numeric"):
        service.execute_conversion("invalid_num", "C", "F")

    # Violation of physical threshold
    with pytest.raises(ValueError, match="Physical violation"):
        service.execute_conversion(-300.0, "C", "K")
