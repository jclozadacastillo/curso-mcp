"""
Service layer for Temperature Conversion.
Coordinates validation, logging, and formatted domain payloads.
"""

from typing import Any, Dict
from .converter import convert_temperature


class TemperatureService:
    """Application service for performing and formatting temperature conversions."""

    def __init__(self, service_name: str = "UNIANDES-TempService"):
        self.service_name = service_name

    def execute_conversion(self, raw_value: Any, from_unit: str, to_unit: str) -> Dict[str, Any]:
        """
        Executes a conversion returning structured payload.
        Handles numeric conversion and raises domain exceptions on failure.
        """
        try:
            val_float = float(raw_value)
        except (ValueError, TypeError) as err:
            raise TypeError(f"Invalid input: '{raw_value}' cannot be converted to numeric temperature.") from err

        result = convert_temperature(val_float, from_unit, to_unit)
        return {
            "service": self.service_name,
            "input_value": val_float,
            "from_unit": str(from_unit).strip().upper(),
            "to_unit": str(to_unit).strip().upper(),
            "result": result,
            "formatted": f"{result:.2f} {str(to_unit).strip().upper()}",
        }
