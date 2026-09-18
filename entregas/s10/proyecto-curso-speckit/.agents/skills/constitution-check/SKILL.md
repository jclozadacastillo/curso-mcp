---
name: constitution-check
description: Usa esta skill al finalizar cualquier tarea de tasks.md, para verificar cumplimiento con la constitución antes de marcarla como terminada.
---
Verifica, en este orden:
1. Capas respetadas (routers -> services -> repositories -> database, utils puras).
2. DIP con parámetro por defecto en `services/` (`repo=gastos_repository`), sin acoplamiento a implementaciones fijas.
3. Si toca datos de usuario, filtro por `usuario_id` resuelto desde el JWT verificado (nunca desde input del cliente).
4. Test correspondiente escrito y en verde (`PASSED`), sin usar `unittest.mock` para el repository.
5. Si toca MCP, reutiliza `services/` sin reimplementar lógica de negocio.
