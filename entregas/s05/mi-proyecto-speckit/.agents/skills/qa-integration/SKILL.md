---
name: qa-integration
description: Audita el test de integracion EN MEMORIA (sin subprocess) existente contra specs/*/spec.md y agrega solo lo que falta, sin improvisar el flujo a probar ni duplicar lo ya cubierto.
---
# Instrucciones
1. Lee `specs/*/spec.md`, seccion "Acceptance Scenarios" — identifica los escenarios que requieren que 2+ modulos de tu propio codigo se conecten (ej. tu CLI llamando a tu logica de negocio). Si no existe ningun `specs/*/spec.md`, DETENTE y pide que se corra Spec Kit primero.
2. Si existe `tests/integration/`, revisa que flujo ya prueba antes de escribir nada. Si algun archivo ahi usa `subprocess` para lanzar el programa completo, NO es integracion — es un test e2e mal clasificado. No lo toques ni lo dupliques: reportalo, la skill `qa-e2e` se encarga de reubicarlo.
3. Si el escenario ya esta cubierto por un test real en memoria, reportalo como "ya cubierto en `<archivo>`" y no lo dupliques.
4. Si falta, agrega un test **en memoria** (llama directamente a las funciones que conectan tus modulos, sin lanzar el programa como proceso aparte) en el archivo existente o en uno nuevo dentro de `tests/integration/`.
5. Corre `uv run pytest tests/integration/ -v` y reporta el resultado.
