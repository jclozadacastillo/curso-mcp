"""
Unit tests generated for mi-proyecto-speckit following specs/temp-converter/spec.md.
"""

import pytest
from src.temp_converter.converter import convert_temperature


def test_scenario_1_celsius_to_fahrenheit():
    # Given 100.0 C -> When converted to F -> Then 212.00
    assert convert_temperature(100.0, "C", "F") == 212.00


def test_scenario_2_fahrenheit_to_celsius():
    # Given 32.0 F -> When converted to C -> Then 0.00
    assert convert_temperature(32.0, "F", "C") == 0.00


def test_scenario_3_celsius_to_kelvin():
    # Given 0.0 C -> When converted to K -> Then 273.15
    assert convert_temperature(0.0, "C", "K") == 273.15


def test_scenario_4_identity_conversion():
    # Given 25.5 C -> When converted to C -> Then 25.50
    assert convert_temperature(25.5, "C", "C") == 25.50


def test_scenario_5_absolute_zero_boundary():
    # Given -273.15 C -> When converted to K -> Then 0.00
    assert convert_temperature(-273.15, "C", "K") == 0.00


def test_scenario_6_rejection_below_absolute_zero():
    # Given -274.0 C -> When converted -> Raises ValueError
    with pytest.raises(ValueError, match="Physical violation"):
        convert_temperature(-274.0, "C", "F")

    with pytest.raises(ValueError, match="Physical violation"):
        convert_temperature(-1.0, "K", "C")


def test_edge_cases_non_numeric():
    with pytest.raises(TypeError):
        convert_temperature("invalid", "C", "F")

    with pytest.raises(TypeError):
        convert_temperature(True, "C", "F")


def test_edge_cases_whitespace_and_invalid_unit():
    assert convert_temperature(100.0, " c ", " f ") == 212.00
    with pytest.raises(ValueError, match="Unsupported"):
        convert_temperature(100.0, "X", "F")


def test_edge_cases_nan_and_inf():
    with pytest.raises(ValueError, match="finite real number"):
        convert_temperature(float("nan"), "C", "F")

    with pytest.raises(ValueError, match="finite real number"):
        convert_temperature(float("inf"), "C", "F")
