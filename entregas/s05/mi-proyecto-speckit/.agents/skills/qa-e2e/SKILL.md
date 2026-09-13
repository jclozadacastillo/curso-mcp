---
name: qa-e2e
description: Audita los tests end-to-end existentes (proceso completo, via subprocess) contra specs/*/spec.md y agrega solo lo que falta, sin improvisar el flujo ni duplicar lo ya cubierto.
---
# Instrucciones
1. Lee `specs/*/spec.md`, seccion "Acceptance Scenarios" — identifica los escenarios que describen el uso real de punta a punta, como lo usaria la persona que opera el programa. Si no existe ningun `specs/*/spec.md`, DETENTE y pide que se corra Spec Kit primero.
2. Revisa `tests/e2e/` (creala si no existe). Ademas, revisa si `tests/integration/` tiene algun archivo que en realidad use `subprocess` para lanzar el programa completo — si lo encuentras, muevelo a `tests/e2e/` con `git mv` (no lo reescribas, solo reubicalo) y avisa que lo hiciste.
3. Para cada escenario que no este cubierto, agrega un test e2e nuevo: invoca el programa completo como lo haria un usuario real (via `subprocess`, verificando stdout y codigo de salida), nunca llamando a una funcion interna directamente.
4. Corre `uv run pytest tests/e2e/ -v` y reporta el resultado.
