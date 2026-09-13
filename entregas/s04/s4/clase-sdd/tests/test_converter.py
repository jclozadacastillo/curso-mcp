"""
Tests unitarios para converter.py basados en spec_manual.md
"""

import pytest
from src.converter import convertir_temperatura


def test_conversion_celsius_a_fahrenheit():
    # 0 C -> 32.0 F
    assert convertir_temperatura(0, "C", "F") == 32.00
    # 100 C -> 212.0 F
    assert convertir_temperatura(100, "C", "F") == 212.00
    # -40 C -> -40.0 F
    assert convertir_temperatura(-40, "C", "F") == -40.00


def test_conversion_fahrenheit_a_celsius():
    assert convertir_temperatura(32, "F", "C") == 0.00
    assert convertir_temperatura(212, "F", "C") == 100.00
    assert convertir_temperatura(-40, "F", "C") == -40.00


def test_conversion_celsius_a_kelvin():
    assert convertir_temperatura(0, "C", "K") == 273.15
    assert convertir_temperatura(100, "C", "K") == 373.15
    assert convertir_temperatura(-273.15, "C", "K") == 0.00


def test_conversion_kelvin_a_celsius():
    assert convertir_temperatura(273.15, "K", "C") == 0.00
    assert convertir_temperatura(0, "K", "C") == -273.15


def test_misma_unidad():
    assert convertir_temperatura(25.5, "C", "C") == 25.50
    assert convertir_temperatura(100.123, "F", "F") == 100.12


def test_rechazo_debajo_cero_absoluto():
    with pytest.raises(ValueError, match="cero absoluto"):
        convertir_temperatura(-274, "C", "K")

    with pytest.raises(ValueError, match="cero absoluto"):
        convertir_temperatura(-1, "K", "C")

    with pytest.raises(ValueError, match="cero absoluto"):
        convertir_temperatura(-460, "F", "C")


def test_tipo_no_numerico():
    with pytest.raises(TypeError):
        convertir_temperatura("100", "C", "F")

    with pytest.raises(TypeError):
        convertir_temperatura(None, "C", "F")
