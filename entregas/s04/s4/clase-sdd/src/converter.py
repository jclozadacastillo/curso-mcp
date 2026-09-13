"""
Conversor de Temperatura
Implementacion basada estrictamente en spec_manual.md
"""

from typing import Union

UNIDADES_VALIDAS = {"C", "F", "K"}
CERO_ABSOLUTO = {
    "C": -273.15,
    "F": -459.67,
    "K": 0.0,
}


def convertir_temperatura(
    valor: Union[int, float],
    desde: str,
    hacia: str,
) -> float:
    """
    Convierte una temperatura entre Celsius (C), Fahrenheit (F) y Kelvin (K).
    Aplica validaciones de limites fisicos y redondeo a 2 decimales.
    """
    # Validacion de tipo
    if not isinstance(valor, (int, float)) or isinstance(valor, bool):
        raise TypeError(f"El valor de temperatura debe ser numerico, se recibio: {type(valor).__name__}")

    desde_u = str(desde).strip().upper()
    hacia_u = str(hacia).strip().upper()

    if desde_u not in UNIDADES_VALIDAS:
        raise ValueError(f"Unidad de origen no soportada: '{desde}'. Use C, F o K.")
    if hacia_u not in UNIDADES_VALIDAS:
        raise ValueError(f"Unidad de destino no soportada: '{hacia}'. Use C, F o K.")

    # Validacion del cero absoluto
    limite = CERO_ABSOLUTO[desde_u]
    if valor < limite:
        raise ValueError(
            f"Temperatura invalida: {valor} {desde_u} se encuentra por debajo del cero absoluto ({limite} {desde_u})."
        )

    # Caso borde: misma unidad
    if desde_u == hacia_u:
        return round(float(valor), 2)

    # Conversion intermedia a Celsius
    if desde_u == "C":
        celsius = float(valor)
    elif desde_u == "F":
        celsius = (valor - 32.0) * (5.0 / 9.0)
    else:  # Kelvin
        celsius = valor - 273.15

    # Conversion desde Celsius a unidad destino
    if hacia_u == "C":
        resultado = celsius
    elif hacia_u == "F":
        resultado = (celsius * (9.0 / 5.0)) + 32.0
    else:  # Kelvin
        resultado = celsius + 273.15

    return round(resultado, 2)
