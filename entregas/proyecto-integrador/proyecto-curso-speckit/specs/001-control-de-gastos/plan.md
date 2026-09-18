# Plan de Implementación — Sistema de Control de Gastos

## Stack Tecnológico
- **Framework Web**: `FastAPI` (>=0.110.0), `uvicorn[standard]`
- **Validación y Configuración**: `pydantic` (>=2.6.0), `pydantic-settings` (>=2.2.0), `email-validator` (>=2.1.0)
- **Persistencia**: `SQLAlchemy` (>=2.0.0), `alembic` (>=1.13.0), SQLite en memoria (tests) y SQLite local en desarrollo
- **Seguridad**: `pyjwt` (>=2.8.0), `passlib[bcrypt]` (>=1.7.4), `bcrypt` (<4.1.0 fijado para compatibilidad con passlib), `python-multipart`
- **MCP (Model Context Protocol)**: SDK oficial de Anthropic / Model Context Protocol (`mcp` >=1.0.0) montado sobre transporte `streamable-http` y soporte `stdio`
- **Testing y Calidad**: `pytest` (>=8.0.0), `pytest-cov` (>=4.1.0), `httpx` (>=0.27.0)

## Trazabilidad Plan → Artículos de la Constitución

### 1. Arquitectura en capas (Artículo I)
- El código se estructura estrictamente en paquetes desacoplados bajo el directorio `app/`:
  - `app/routers/`: Reciben peticiones HTTP, validan parámetros con Pydantic, llaman a `services/` y mapean excepciones de dominio a códigos HTTP (`HTTPException`).
  - `app/services/`: Contienen el 100% de las reglas de negocio (monto > 0, categorías permitidas, límite acumulado de 500). Nunca importan SQLAlchemy ni Sessions directamente.
  - `app/repositories/`: Exclusivos para interactuar con la base de datos SQLAlchemy. Módulos con funciones (`guardar`, `listar`, `total_por_categoria`), sin lógica de negocio, devolviendo diccionarios o modelos de dominio.
  - `app/utils/`: Funciones puras (hashing, generación y validación de tokens JWT), sin dependencias hacia capas superiores.
  - `app/mcp/tools/`: Herramientas MCP que delegan directamente en las funciones de `app/services/`, sin duplicar lógica de negocio.

### 2. SOLID aplicado y DIP (Artículo II)
- **SRP (Responsabilidad Única)**: Cada servicio desglosa su validación (`_validar_monto`, `_validar_categoria`, `_validar_limite`) de la acción principal (`registrar_gasto`).
- **OCP (Abierto/Cerrado)**: Las categorías permitidas se definen mediante un `Enum` (`CategoriaEnum`) o tupla inmutable de constantes en `app/models/gasto.py`.
- **DIP (Inversión de Dependencias)**: En `services/gastos.py`, toda función que requiere persistencia recibe el repositorio como parámetro por defecto:
  ```python
  def registrar_gasto(db, usuario_id, descripcion, monto, categoria, repo=gastos_repository) -> dict: ...
  def listar_gastos(db, usuario_id, skip=0, limit=20, repo=gastos_repository) -> list[dict]: ...
  ```
  Esto permite inyectar repositorios simulados (`RepositorioFalso`) en tests unitarios sin recurrir a `unittest.mock`.

### 3. Persistencia y Aislamiento Multiusuario (Artículo III)
- Modelos ORM declarados con `SQLAlchemy` declarative base en `app/models/`:
  - `Usuario`: `id`, `email` (indexado, único), `hashed_password`.
  - `Gasto`: `id`, `descripcion`, `monto`, `categoria`, `usuario_id` (ForeignKey `usuarios.id`, nullable=False).
- Toda consulta de gastos ejecutada en `repositories/gastos.py` incluye obligatoriamente el filtro `.filter(GastoModel.usuario_id == usuario_id)`.
- Compatibilidad Postgres/SQLite en `app/database.py` mediante configuración condicional de `connect_args={"check_same_thread": False}` solo para URLs con dialecto SQLite.

### 4. Seguridad Estricta (Artículo IV)
- Hash de contraseñas mediante `CryptContext(schemes=["bcrypt"], deprecated="auto")` con `bcrypt<4.1`.
- Autenticación OAuth2 Password Flow (`OAuth2PasswordBearer(tokenUrl="/usuarios/token")`) y JWT firmado con algoritmo `HS256`.
- Secretos gestionados con `pydantic_settings.BaseSettings` leyendo exclusivamente de `.env`. Archivo `.env.example` versionado con variables descriptivas (`SECRET_KEY`, `DATABASE_URL`, `ACCESS_TOKEN_EXPIRE_MINUTES`).
- Enrutamiento y autorización: La identidad del usuario (`usuario_id`) se extrae única y exclusivamente desde `get_current_user` decodificando el claim `sub` del JWT. Ningún router ni servicio acepta `usuario_id` como input del payload o query string.
- Manejo de excepciones no controladas: Exception handler global en FastAPI que devuelve `500` con `{"detail": "Error interno del servidor"}`, registrando el stack trace únicamente en los logs internos.

### 5. Diseño de Endpoints REST (Artículo V)
- Códigos HTTP semánticos: `POST /usuarios/` (201), `POST /usuarios/token` (200), `POST /gastos/` (201), `GET /gastos/` (200). Errores de dominio mapeados a 400 Bad Request, credenciales inválidas a 401, rutas no autorizadas a 403 (en `PATCH /gastos/{id}`).
- Separación de esquemas Pydantic: `GastoCreate` (entrada: `descripcion`, `monto`, `categoria`) vs `GastoOut` (salida: `id`, `descripcion`, `monto`, `categoria`, `usuario_id`). Nunca se retorna el modelo ORM directamente.
- Paginación estándar: Parámetros `skip: int = 0` y `limit: int = 20` con validación de valores no negativos.

### 6. Integración MCP (Artículo VI)
- Servidor MCP configurado en `app/mcp/server.py` y tools en `app/mcp/tools/gastos.py`.
- Reutilización total: Las tools `registrar_gasto` y `listar_gastos` llaman a las mismas funciones de `app/services/gastos.py`.
- Descripciones de tools claras, accionables y contextualizadas.
- Manejo de errores de dominio en MCP mediante retorno estructurado `{"error": str(e)}`.
- Propagación de identidad: Se decodifica el token Bearer en solicitudes `streamable-http`; fallback a usuario demo documentado para transporte `stdio`.

### 7. Estrategia de Testing y Cobertura (Artículo VII)
- Suite organizada en:
  - `tests/test_gastos.py`: Pruebas unitarias de `services/` con `RepositorioFalso` (sin mocks).
  - `tests/test_integracion_gastos.py`: Pruebas de integración contra base de datos SQLite en memoria (`sqlite:///:memory:`).
  - `tests/test_api_gastos.py`: Pruebas de integración de endpoints REST usando `TestClient` y `app.dependency_overrides`.
  - `tests/test_auth_casos.py`: Cobertura explícita de los casos de error 4 (401 sin token) y 5 (intento de suplantación de `usuario_id`).
  - `tests/test_mcp_gastos.py`: Pruebas unitarias de tools MCP (caso exitoso y caso de error).
- Cobertura exigida:
  - Líneas de `app/services/` ≥ 90%.
  - Líneas globales del conjunto `services + repositories + routers + utils` ≥ 80%.
  - Declaración explícita de exclusiones en `pyproject.toml` (`[tool.coverage.run] omit = ["app/main.py", "app/mcp/server.py", "app/logging_config.py"]`).

### 8. Compatibilidad con Referencia de S6-S8 (Artículo VIII)
- Respeto irrestricto de las firmas, tipos y módulos especificados en el contrato de compatibilidad de `spec.md`.
- Existencia de `tests/__init__.py` para soportar importaciones de `RepositorioFalso` en `test_api_gastos.py`.
