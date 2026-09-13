---
name: qa-coverage
description: Ejecuta y resume el reporte de cobertura de tests del proyecto, senalando lineas sin probar.
---
# Instrucciones
1. Corre `uv run pytest --cov=src --cov-report=term-missing` (ajusta `src` si tu codigo no vive bajo esa carpeta).
2. Resume: porcentaje total, y que lineas "Missing" son casos borde olvidados vs. codigo no usado.
3. No agregues tests automaticamente — solo diagnostica.
