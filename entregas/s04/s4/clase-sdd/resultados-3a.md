# Resultados de Pruebas — Bloque 3.A (Spec a mano)

**Proyecto:** Conversor de Temperatura  
**Modulo:** `clase-sdd`  
**Ejecutado por:** Juan Carlos Lozada (UNIANDES)  

---

## 1. Casos Evaluados

### Caso 1 — Uso Normal (Tipico y Esperado)
* **Entrada:** `convertir_temperatura(100.0, 'C', 'F')`
* **Comportamiento esperado:** 212.00 °F
* **Resultado real:** `212.0` (redondeado formalmente a 2 decimales)
* **Estado:** APROBADO (cumple formula estandar $(100 \times 9/5) + 32 = 212$).

### Caso 2 — Caso Borde Definido en la Spec
* **Entrada:** `convertir_temperatura(-273.15, 'C', 'K')` (limite exacto del cero absoluto)
* **Comportamiento esperado:** 0.00 K sin arrojar excepcion.
* **Resultado real:** `0.0`
* **Estado:** APROBADO (la validacion `< -273.15` permitio exactamente el limite sin rechazarlo por redondeo de coma flotante).

### Caso 3 — Caso No Contemplado en la Spec
* **Entrada:** `convertir_temperatura(float('inf'), 'C', 'F')` (paso de infinito como float valido)
* **Comportamiento esperado (no especificado):** La spec no definio que hacer con infinitos o NaN.
* **Resultado real:** Devuelve `inf` sin lanzar error, propagando el valor infinito.
* **Comportamiento con unidad no contemplada (ej. Rankine 'R'):** Lanza `ValueError: Unidad de origen no soportada: 'R'. Use C, F o K.`
* **Observacion critica:** Al no explicitar en la spec manual el tratamiento de `math.isnan()` o `math.isinf()`, el codigo acepta valores no fisicos sin protestar.

---

## 2. Resumen de Suite Automatizada
* **Comando:** `uv run pytest tests/test_converter.py -v`
* **Total ejecutado:** 7 tests
* **Aprobados:** 7 (100%)
* **Tiempo:** 0.02s
