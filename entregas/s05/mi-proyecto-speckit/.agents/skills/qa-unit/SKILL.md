---
name: qa-unit
description: Audita los tests unitarios existentes contra specs/*/spec.md (Acceptance Scenarios, Edge Cases, Functional Requirements) y agrega solo lo que falta, sin improvisar que probar ni duplicar lo ya cubierto.
---
# Instrucciones
1. Lee `specs/*/spec.md` — secciones "Acceptance Scenarios", "Edge Cases" y "Functional Requirements" (revisa tambien `## Clarifications` si existe: ahi suelen vivir los requisitos agregados despues de la implementacion original). Si no existe ningun `specs/*/spec.md`, DETENTE y pide que se corra Spec Kit primero — no inventes criterios propios.
2. Si existe `tests/unit/`, revisa los tests que ya hay ahi antes de escribir nada.
3. Para cada escenario, caso borde o FR que corresponda a una funcion aislada: si ya hay un test que lo cubre, reportalo como "ya cubierto en `<archivo>`" y no lo dupliques. Si no esta cubierto, agregalo con un assert real — dentro del archivo de `tests/unit/` que corresponda por tema, o en uno nuevo si no encaja en ninguno.
4. No agregues tests para casos que no esten en la spec — si crees que falta algo importante, sugierelo al final, no lo generes por tu cuenta.
5. Corre `uv run pytest tests/unit/ -v` y reporta cuantos pasaron, cuantos fallaron, y cuantos tests eran nuevos.
