"""
Command-line interface for the temperature converter.
Allows terminal invocations with exit codes and stdout reporting.
"""

import argparse
import sys
from .service import TemperatureService


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Conversor de Temperatura UNIANDES")
    parser.add_argument("--value", type=float, required=True, help="Valor de temperatura a convertir")
    parser.add_argument("--from", dest="from_unit", type=str, required=True, help="Unidad origen (C, F, K)")
    parser.add_argument("--to", dest="to_unit", type=str, required=True, help="Unidad destino (C, F, K)")
    return parser


def main(argv=None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)

    service = TemperatureService()
    try:
        data = service.execute_conversion(args.value, args.from_unit, args.to_unit)
        print(data["formatted"])
        return 0
    except (ValueError, TypeError) as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
