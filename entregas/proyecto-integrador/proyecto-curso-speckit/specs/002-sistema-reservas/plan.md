# Plan de Implementación Técnica: Sistema de Gestión y Reserva de Espacios
**Feature ID:** `002-sistema-reservas`  
**Metodología:** Spec-Driven Development (SDD) con Spec-Kit y Google Antigravity (`agy`)

---

## 1. Arquitectura Técnica y Stack Tecnológico

| Componente | Selección Tecnológica | Justificación Constitucional |
|---|---|---|
| **Framework Web** | FastAPI (`>=0.110.0`) | Provee validación automática con Pydantic, generación OpenAPI/Swagger y middleware OAuth2 (Art. I.1, Art. V). |
| **Validación y Configuración** | Pydantic v2 + Pydantic-Settings | Esquemas estrictos de entrada/salida y lectura tipada de variables de entorno desde `.env` (Art. IV.4, Art. V.2). |
| **ORM y Persistencia** | SQLAlchemy 2.0 (`mapped_column`) | Modelado desacoplado, soporte de transacciones y portabilidad SQLite/PostgreSQL (Art. III.1). |
| **Criptografía y Seguridad** | `passlib[bcrypt]` (`bcrypt<4.1.0`) + `pyjwt` | Algoritmo bcrypt para almacenamiento no reversible de contraseñas y firma HMAC-SHA256 de tokens de acceso (Art. IV.1, Art. IV.2). |
| **Protocolo de IA (MCP)** | SDK oficial `mcp` (`FastMCP`) | Exposición de herramientas semánticas reutilizando `services/` con contratos estructurados (Art. VI.1, Art. VI.2). |
| **Testing y Métricas** | `pytest`, `pytest-cov`, `httpx` (`TestClient`) | Ejecución de pirámide de pruebas, aserciones sin mocks sobre `services/` y certificación de cobertura (Art. II.4, Art. VII). |

---

## 2. Matriz de Trazabilidad: Decisión Técnica $\to$ Artículo Constitucional

1. **Monolito modular en capas (`routers/`, `services/`, `repositories/`, `models/`, `schemas/`, `mcp/`):**
   * *Satisface:* **Artículo I (Arquitectura en Capas).**
   * *Detalle:* `routers/reservas.py` solo valida peticiones HTTP y mapea códigos; `services/reservas.py` orquesta la lógica de negocio pura; `repositories/reservas.py` interactúa con el motor SQLAlchemy.
2. **Inyección de dependencias por parámetro con implementación falsa en tests:**
   * *Satisface:* **Artículo II.3 y II.4 (DIP y Prohibición de Mocks).**
   * *Detalle:* `crear_reserva(..., repo: ReservaRepository = reserva_repository)` permite inyectar `RepositorioFalsoReservas` en tests unitarios, desacoplando la lógica de la base de datos sin incurrir en acoplamiento de `unittest.mock`.
3. **Clave foránea `usuario_id` y consultas filtradas por usuario:**
   * *Satisface:* **Artículo III.3 (Aislamiento Multiusuario).**
   * *Detalle:* Toda búsqueda en `repositories/reservas.py` para un usuario incluye `.filter(Reserva.usuario_id == usuario_id)`.
4. **Extracción de `usuario_id` desde `get_current_user`:**
   * *Satisface:* **Artículo IV.3 (Seguridad e Identidad Confiable).**
   * *Detalle:* El cliente jamás envía `usuario_id` en el body o query. El endpoint extrae el ID únicamente tras decodificar y validar el JWT.
5. **Códigos de estado HTTP semánticos (201, 200, 204, 400, 401, 403, 404, 422):**
   * *Satisface:* **Artículo V.1 (Convención REST).**
   * *Detalle:* Se capturan excepciones de dominio (`HorarioInvalidoError`, `SolapamientoReservaError`, `PermisoDenegadoError`, `ReservaNoEncontradaError`, `AccionNoConfirmadaError`) y se traducen a sus respectivos códigos de error.
6. **Reutilización directa de `services/` en MCP Tools y confirmación destructiva:**
   * *Satisface:* **Artículo VI.1, VI.2 y VI.4 (Herramientas MCP).**
   * *Detalle:* `app/mcp/tools/reservas.py` invoca exactamente las mismas funciones de `app/services/reservas.py`. La cancelación exige `confirmacion=True` validado por el servicio.
7. **Cobertura de pruebas $\ge 90\%$ en `services/` y $\ge 70\%$ global:**
   * *Satisface:* **Artículo VII.3 (Estándar de Testing).**
   * *Detalle:* Configuración estricta en `pyproject.toml` (`[tool.coverage.run]`) y reporte de líneas no cubiertas.

---

## 3. Diagrama de Flujo de la Regla de Negocio Central (Anti-Solapamiento)

```text
[Cliente REST / MCP]
        |
        v
[services.reservas.crear_reserva]
        |
        +---> Validar hora_fin > hora_inicio (RN-02) --> Si no: raise HorarioInvalidoError (400)
        |
        +---> Validar fecha >= hoy (RN-02b) ---------> Si no: raise HorarioInvalidoError (400)
        |
        +---> Obtener reservas del espacio y fecha via repo.obtener_por_espacio_y_fecha(espacio, fecha)
        |
        +---> Evaluar intersección temporal:
        |     Para cada reserva r:
        |       max(r.hora_inicio, nueva.hora_inicio) < min(r.hora_fin, nueva.hora_fin)
        |       --> Si True: raise SolapamientoReservaError (400) (RN-01)
        |
        +---> Si no hay solapamiento (o se tocan en el borde exacto) (RN-01b):
              repo.crear(nueva_reserva)
              return reserva_guardada
```
