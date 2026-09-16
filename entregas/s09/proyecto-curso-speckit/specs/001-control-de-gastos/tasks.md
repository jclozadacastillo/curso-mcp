# Lista de Tareas — Implementación Spec-Driven: Sistema de Control de Gastos

Todas las tareas se ejecutan siguiendo la siguiente **Definition of Done (DoD)** obligatoria:
1. Código fuente implementado cumpliendo estrictamente la arquitectura en capas.
2. Test automatizado escrito y pasando en verde (`PASSED`).
3. Verificación de no violación de ningún artículo de `constitution.md`.

---

## Fase 1 — Configuración del Entorno, Seguridad y Persistencia Base
- [ ] **T01: Configuración de dependencias y políticas de cobertura**
  - *Archivos*: `pyproject.toml`, `.env.example`, `.env`
  - *Test*: `uv run pytest --version`
  - *DoD*: `pyproject.toml` incluye configuración de pytest, pytest-cov y la directiva `[tool.coverage.run] omit` para exclusiones declaradas (Artículo VII.3).
- [ ] **T02: Configuración de Base de Datos y Sesión SQLAlchemy**
  - *Archivos*: `app/database.py`, `app/config.py`
  - *Test*: `tests/test_database.py::test_database_connection`
  - *DoD*: Conexión SQLite con `connect_args` condicional, sesión `SessionLocal` y generador `get_db` compatible con PostgreSQL (Artículo III.2).

## Fase 2 — Modelos ORM y Schemas Pydantic
- [ ] **T03: Modelos SQLAlchemy para Usuario y Gasto**
  - *Archivos*: `app/models/usuario.py`, `app/models/gasto.py`
  - *Test*: `tests/test_models.py::test_models_creation`
  - *DoD*: `Usuario` con `email` único; `Gasto` con `usuario_id` como ForeignKey obligatoria (Artículo III.3).
- [ ] **T04: Schemas Pydantic separados de entrada y salida**
  - *Archivos*: `app/schemas/usuario.py`, `app/schemas/gasto.py`
  - *Test*: `tests/test_schemas.py::test_schema_validations`
  - *DoD*: `GastoCreate` no expone `id` ni `usuario_id`. `GastoOut` incluye `id` y serializa sin exponer SQLAlchemy (Artículo V.3).

## Fase 3 — Capa de Repositorios (Persistencia desacoplada)
- [ ] **T05: Repositorio de Usuarios (módulo con funciones)**
  - *Archivos*: `app/repositories/usuarios.py`
  - *Test*: `tests/test_integracion_usuarios.py::test_guardar_y_obtener_usuario`
  - *DoD*: Funciones `guardar(db, email, hashed_password)` y `obtener_por_email(db, email)`. Sin lógica de negocio (Artículo I.3, VIII.2).
- [ ] **T06: Repositorio de Gastos (módulo con funciones)**
  - *Archivos*: `app/repositories/gastos.py`
  - *Test*: `tests/test_integracion_gastos.py::test_guardar_listar_total`
  - *DoD*: Funciones `guardar`, `listar`, `total_por_categoria`. Todo query filtra por `usuario_id`. Devuelven `dict`, no objetos ORM (Artículo I.3, III.3, VIII.2).

## Fase 4 — Capa de Servicios y Reglas de Negocio (DIP)
- [ ] **T07: Servicio de Gastos con Inversión de Dependencias (DIP) y Casos 1, 2 y 3**
  - *Archivos*: `app/services/gastos.py`
  - *Test*: `tests/test_gastos.py::test_registrar_gasto_exito`, `test_monto_invalido`, `test_categoria_invalida`, `test_limite_excedido`
  - *DoD*: `CategoriaInvalidaError`, `LimiteExcedidoError`, `LIMITE_POR_CATEGORIA = 500.0`. Inyección de `repo=gastos_repository` por defecto. Testeado con `RepositorioFalso` sin `unittest.mock` (Artículo I.2, II.1, II.3, VII.2, VII.3).
- [ ] **T08: Servicio de Usuarios y Autenticación**
  - *Archivos*: `app/services/usuarios.py`
  - *Test*: `tests/test_services_usuarios.py::test_crear_usuario_y_autenticar`
  - *DoD*: Registro con validación de email duplicado (`EmailDuplicadoError`) y validación de credenciales (Artículo I.2, IV.1).

## Fase 5 — Utilidades Puras y Dependencias de Seguridad
- [ ] **T09: Utilidades de Criptografía y JWT**
  - *Archivos*: `app/utils/security.py`
  - *Test*: `tests/test_security.py::test_password_hashing_and_jwt`
  - *DoD*: Funciones puras con `passlib[bcrypt]` y `pyjwt`. Hashing seguro y verificación de expiración (Artículo I.4, IV.1, IV.2).
- [ ] **T10: Dependencias de Seguridad FastAPI**
  - *Archivos*: `app/dependencies.py`
  - *Test*: `tests/test_dependencies.py::test_get_current_user`
  - *DoD*: `get_current_user` extrae el `usuario_id` del token JWT. `get_gastos_repo` para DI (Artículo IV.4).

## Fase 6 — Routers REST, Manejo de Errores y Casos 4 y 5
- [ ] **T11: Router de Usuarios y Autenticación**
  - *Archivos*: `app/routers/usuarios.py`
  - *Test*: `tests/test_api_usuarios.py::test_registro_y_login_token`
  - *DoD*: `POST /usuarios/` (201), `POST /usuarios/token` (200 con JWT). Mapeo de errores a 400 y 401 (Artículo V.1).
- [ ] **T12: Router de Gastos y compatibilidad con `test_api_gastos.py`**
  - *Archivos*: `app/routers/gastos.py`, `app/main.py`
  - *Test*: `tests/test_api_gastos.py`
  - *DoD*: `POST /gastos/` (201) y `GET /gastos/` (200). Compatible con los tests de S6-S8 sin alterar aserciones (Artículo V.1, VIII.1).
- [ ] **T13: Tests de Seguridad REST (Casos de Error 4 y 5)**
  - *Archivos*: `tests/test_auth_casos.py`
  - *Test*: `tests/test_auth_casos.py::test_acceso_sin_token_retorna_401`, `test_usuario_id_ajeno_es_ignorado`
  - *DoD*: Caso 4 (petición sin token -> 401) y Caso 5 (`usuario_id` ajeno en payload o query no afecta el filtrado por el JWT del usuario autenticado) (Artículo IV.4, VII.3).

## Fase 7 — Reto Opcional: Actualización de Categoría con Criterios Verificables
- [ ] **T14: Endpoint PATCH /gastos/{id} y service `actualizar_categoria`**
  - *Archivos*: `app/services/gastos.py`, `app/routers/gastos.py`
  - *Test*: `tests/test_actualizar_categoria.py`
  - *DoD*: Verificación de propiedad (403 si no es dueño, 404 si no existe), validación de categoría (400), registro en logs de auditoría (Artículo IV.4, V.1).

## Fase 8 — Integración de Herramientas MCP
- [ ] **T15: Tools MCP de Gastos y Manejo Estructurado de Errores**
  - *Archivos*: `app/mcp/tools/gastos.py`, `app/mcp/server.py`
  - *Test*: `tests/test_mcp_gastos.py::test_mcp_registrar_gasto_exito`, `test_mcp_error_negocio`
  - *DoD*: Tools `registrar_gasto` y `listar_gastos` reutilizan `services/gastos.py`. Errores de negocio retornados como `{"error": "..."}`. Identidad resuelta vía JWT o usuario demo documentado para stdio (Artículo VI.1, VI.2, VI.3, VI.4, VII.6).

## Fase 9 — Verificación Final de Cobertura y Conformidad
- [ ] **T16: Verificación integral de la suite y reporte de cobertura**
  - *Comando*: `uv run pytest --cov=app --cov-report=term-missing -v`
  - *DoD*: 
    1. 100% de los tests en verde (unitarios, integración, API, casos 4 y 5, MCP, y tests de compatibilidad S6-S8).
    2. Cobertura de líneas en `app/services/` ≥ 90%.
    3. Cobertura global (`services + repositories + routers + utils`) ≥ 80%.
    4. Cero violaciones a los 8 artículos de `constitution.md`.
