# Especificacion Manual — Conversor de Temperatura
**Modulo:** `clase-sdd`  
**Autor:** Juan Carlos Lozada  
**Proyecto:** Conversor de Unidades Termicas  

---

## Objetivo
Convertir una temperatura entre las escalas Celsius, Fahrenheit y Kelvin con validacion de limites fisicos y precision decimal.

---

## Criterios de Aceptacion
- [ ] Convierte correctamente de Celsius a Fahrenheit y viceversa mediante formulas estandar.
- [ ] Convierte correctamente de Celsius a Kelvin y viceversa considerando la constante 273.15.
- [ ] Redondea todo resultado final a exactamente 2 posiciones decimales.
- [ ] Rechaza cualquier temperatura inferior al cero absoluto (0.0 K, -273.15 °C, -459.67 °F) levantando `ValueError`.

---

## Casos Borde
- **Entrada no numerica (ej. "abc", None):** Debe arrojar `TypeError` o `ValueError` con mensaje claro de error.
- **Misma unidad de origen y destino (ej. Celsius a Celsius):** Debe retornar el mismo valor redondeado a 2 decimales sin operaciones innecesarias.
- **Temperatura en el cero absoluto exacto (-273.15 °C o 0 K):** Debe procesarse correctamente sin error (ej. -273.15 °C -> 0.00 K).
- **Temperaturas negativas dentro del rango valido (ej. -40 °C):** Deben procesarse sin perdida de signo ni redondeos anomalos (-40.00 °C -> -40.00 °F).
