# Especificación — Sistema de Control de Gastos Personales

## Entidades
- **Usuario**: `email` (único, formato email válido), `hashed_password` (nunca expuesta en respuestas, serialización o logs).
- **Gasto**: `id` (entero), `descripcion` (string no vacío), `monto` (float > 0), `categoria` (string dentro de las categorías válidas), `usuario_id` (FK que referencia al usuario dueño), `fecha` (datetime/date de creación).

## Reglas de negocio
1. **Categorías válidas**: `comida`, `transporte`, `entretenimiento`, `otros`. Cualquier otra categoría es un error de negocio (`CategoriaInvalidaError`), nunca una excepción genérica no controlada.
2. **Monto y descripción**: El monto de un gasto debe ser estrictamente mayor a cero (`monto > 0`); una descripción vacía o de solo espacios también es inválida.
3. **Límite acumulado mensual**: Un gasto no puede hacer que el total acumulado de su categoría supere `500.0` para el usuario en el periodo (`LimiteExcedidoError`).
4. **Aislamiento por usuario**: Un usuario solo puede ver y crear gastos propios; nunca los de otro usuario, sin importar qué identificador se pase en la solicitud.
5. **Autenticación requerida**: Todas las operaciones sobre gastos exigen autenticación válida mediante JWT.

## Contrato de la API (REST)

| Método | Ruta | Auth | Request | Éxito | Errores esperados |
|---|---|---|---|---|---|
| POST | `/usuarios/` | No | `email`, `password` (JSON) | 201 Usuario (`id`, `email`) | 400 email duplicado, 422 validación schema |
| POST | `/usuarios/token` | No | `username`, `password` (`application/x-www-form-urlencoded`) | 200 token JWT (`access_token`, `token_type`) | 401 credenciales inválidas |
| POST | `/gastos/` | Sí (Bearer JWT) | `descripcion`, `monto`, `categoria` (JSON) | 201 Gasto (`id`, `descripcion`, `monto`, `categoria`, `usuario_id`) | 400 categoría inválida, 400 límite excedido, 401 sin token/inválido, 422 validación |
| GET | `/gastos/` | Sí (Bearer JWT) | Query params: `skip` (default 0), `limit` (default 20) | 200 lista `[GastoOut]` | 401 sin token/inválido, 422 skip/limit inválidos |
| PATCH | `/gastos/{id}` | Sí (Bearer JWT) | `categoria` (JSON) | 200 Gasto actualizado | 400 categoría inválida, 401 sin token, 403 gasto de otro usuario, 404 no existe |

## Contrato equivalente por MCP
- Tool `registrar_gasto(descripcion: str, monto: float, categoria: str)`:
  - Mismo comportamiento y mismas reglas de negocio que `POST /gastos/`.
  - Devuelve el gasto creado o una estructura de error de negocio `{ "error": "..." }`.
  - Descripción accionable: "Registra un gasto con descripción, monto y categoría, validando que el monto sea positivo, la categoría válida y que no exceda el límite acumulado de 500 por categoría."
- Tool `listar_gastos(skip: int = 0, limit: int = 20)`:
  - Mismo comportamiento que `GET /gastos/`.
  - Devuelve lista de gastos correspondientes al usuario de la sesión.
- Tool `actualizar_categoria(gasto_id: int, nueva_categoria: str)`:
  - Mismo comportamiento que `PATCH /gastos/{id}`.
- **Manejo de identidad en MCP**:
  - Ambas tools operan siempre sobre el usuario autenticado de la sesión MCP.
  - Si el transporte es `streamable-http`, la identidad se resuelve desde el token JWT verificado en el header `Authorization`.
  - Si el transporte es `stdio` y no hay propagación de token, se documenta explícitamente en el código como simplificación consciente el uso del usuario demo configurado en `.env`. Nunca se acepta `usuario_id` como parámetro de la tool.

## Contrato de compatibilidad (no negociable)
Los tests de las Sesiones 6-8 se copian sin modificar y fijan las siguientes firmas exactas:

- `app/services/gastos.py`:
  - `CategoriaInvalidaError(Exception)`
  - `LimiteExcedidoError(Exception)`
  - `LIMITE_POR_CATEGORIA = 500.0`
  - `registrar_gasto(db, usuario_id, descripcion, monto, categoria, repo=gastos_repository) -> dict`
  - `listar_gastos(db, usuario_id, skip=0, limit=20, repo=gastos_repository) -> list[dict]`
  *(orden posicional exacto, `repo` es keyword con valor por defecto según DIP)*
- `app/repositories/gastos.py` (módulo con funciones sueltas, NO clase):
  - `guardar(db, usuario_id, descripcion, monto, categoria) -> dict`
  - `listar(db, usuario_id, skip=0, limit=20) -> list[dict]`
  - `total_por_categoria(db, usuario_id, categoria) -> float`
  *(Devuelven `dict`, nunca objetos ORM crudos ni sesiones de SQLAlchemy)*
- `app/repositories/usuarios.py`:
  - `obtener_por_email(db, email) -> Usuario | None`
  - `guardar(db, email, hashed_password) -> Usuario`
- `app.database.get_db`, `app.dependencies.get_current_user`, `app.dependencies.get_gastos_repo`, `app.models.usuario.Usuario(id=, email=, hashed_password=)`: importados directamente por los tests.
- `tests/__init__.py` debe existir: `test_api_gastos.py` hace `from tests.test_gastos import RepositorioFalso`.

## Casos de error explícitos que deben tener test
1. **Caso 1**: Registrar gasto con monto negativo o cero (`monto <= 0`) → Error de validación / rechazo de negocio.
2. **Caso 2**: Registrar gasto con categoría inexistente / inválida → `CategoriaInvalidaError` (HTTP 400 o `{"error": "..."}`).
3. **Caso 3**: Registrar gasto que hace que el total acumulado supere 500 en su categoría → `LimiteExcedidoError` (HTTP 400 o `{"error": "..."}`).
4. **Caso 4**: Listar o registrar gastos sin token JWT o con token inválido/expirado → HTTP 401 Unauthorized.
5. **Caso 5**: Intentar listar o acceder a gastos de otro usuario pasando su ID manualmente → Se ignora el ID ajeno y solo se devuelven los recursos del usuario autenticado en el token (autorización estricta).

## Reto Opcional (Paso 4): Especificación con Criterios Verificables
Para la funcionalidad de corrección de categoría (`actualizar_categoria`):
```markdown
### actualizar_categoria(gasto_id, nueva_categoria)
- DUEÑO: Solo el usuario dueño del gasto puede actualizarlo -> 403 Forbidden si no lo es; 404 si el gasto no existe.
- VALIDACIÓN: nueva_categoria debe pertenecer a [comida, transporte, entretenimiento, otros] -> 400 Bad Request si no.
- LOG / AUDITORÍA: Cada cambio registra usuario_id, gasto_id y categoria_anterior en el sistema de logging.
```

## Aclaraciones resueltas vía `/speckit-clarify`
1. **Roles y Privilegios**: ¿Existen roles de administrador capaces de consultar o modificar gastos ajenos?
   * *Decisión*: No. El modelo es estrictamente monousuario por recurso. No hay roles admin que eludan el aislamiento de datos.
2. **Formato de errores MCP**: ¿Cómo deben comunicarse las excepciones de negocio a los agentes MCP?
   * *Decisión*: Deben atraparse y devolverse como un diccionario estructurado `{"error": str(e)}` con status legible, previniendo que la conexión MCP caiga por excepciones no capturadas.
3. **Persistencia del Gasto**: ¿La fecha del gasto la envía el cliente o la genera el servidor?
   * *Decisión*: El servidor asigna la fecha y hora de creación por defecto (`datetime.now(timezone.utc)`), asegurando coherencia temporal.
