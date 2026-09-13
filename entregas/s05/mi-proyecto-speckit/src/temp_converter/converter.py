"""
Core conversion logic for temperature units.
Pure domain functions adhering to thermodynamics rules.
"""

import math
from typing import Union

SUPPORTED_UNITS = {"C", "F", "K"}
ABSOLUTE_ZERO = {
    "C": -273.15,
    "F": -459.67,
    "K": 0.0,
}


def convert_temperature(
    value: Union[int, float],
    from_unit: str,
    to_unit: str,
) -> float:
    """
    Converts temperature between Celsius, Fahrenheit and Kelvin.
    Enforces absolute zero threshold and rounds to 2 decimal places.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"Temperature value must be numeric, got: {type(value).__name__}")

    if math.isnan(value) or math.isinf(value):
        raise ValueError("Temperature value must be a finite real number.")

    src = str(from_unit).strip().upper()
    dst = str(to_unit).strip().upper()

    if src not in SUPPORTED_UNITS:
        raise ValueError(f"Unsupported source scale: '{from_unit}'. Allowed: C, F, K.")
    if dst not in SUPPORTED_UNITS:
        raise ValueError(f"Unsupported target scale: '{to_unit}'. Allowed: C, F, K.")

    min_val = ABSOLUTE_ZERO[src]
    if value < min_val:
        raise ValueError(
            f"Physical violation: {value} {src} is below absolute zero ({min_val} {src})."
        )

    if src == dst:
        return round(float(value), 2)

    # Base scale: Celsius
    if src == "C":
        celsius = float(value)
    elif src == "F":
        celsius = (value - 32.0) * (5.0 / 9.0)
    else:  # Kelvin
        celsius = value - 273.15

    # Target conversion
    if dst == "C":
        result = celsius
    elif dst == "F":
        result = (celsius * (9.0 / 5.0)) + 32.0
    else:  # Kelvin
        result = celsius + 273.15

    return round(result, 2)
