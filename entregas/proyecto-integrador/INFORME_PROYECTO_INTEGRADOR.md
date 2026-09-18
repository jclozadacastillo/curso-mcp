# Informe de Entrega — Proyecto Integrador (Sesión 10)
**Curso:** MOD2: Programación de Backend y MCP en Python para IA Generativa (08-26)  
**Tema:** Sistema de Gestión y Reserva de Espacios (Consultorios, Salas y Canchas) con Spec-Driven Development, Arquitectura en Capas, OAuth2/JWT y Servidor MCP  
**Estudiante:** Juan Carlos Lozada  
**Institución:** Universidad Regional Autónoma de Los Andes (UNIANDES) / CEDIA  
**Departamento:** Desarrollo de Software  
**Fecha de entrega:** 18 de septiembre de 2026  
**Repositorio GitHub:** [https://github.com/jclozadacastillo/curso-mcp/tree/master/entregas/proyecto-integrador](https://github.com/jclozadacastillo/curso-mcp/tree/master/entregas/proyecto-integrador)  

---

## Resumen Ejecutivo

El presente proyecto integrador implementa un sistema backend de producción y un servidor bajo el **Model Context Protocol (MCP)** para la administración y reserva de espacios compartidos (salas de conferencias, consultorios médicos y canchas deportivas). El desarrollo fue guiado de principio a fin por la metodología **Spec-Driven Development (SDD)** asistida por **Google Antigravity (`agy`)** y el conjunto de herramientas **Spec-Kit**, estableciendo especificaciones formales no negociables antes de generar cualquier línea de código de producción.

A diferencia del caso formativo "Control de Gastos", este proyecto transfirió con éxito los principios arquitectónicos, de seguridad y de pruebas a un nuevo dominio de negocio complejo, resolviendo solapamiento de intervalos temporales en tiempo real, aislamiento multiusuario estricto, confirmación gestionada por el servidor para operaciones destructivas y exposición dual y consistente de capacidades mediante **API REST** y **Tools MCP**.

### Métricas Clave de Evaluación y Verificación
* **Total de Pruebas Automatizadas:** 72 tests ejecutados / 0 fallidos (**100% de aprobación**).
* **Cobertura en Capa de Servicios (`app/services/reservas.py`):** **100.0%** (supera con creces el requisito constitucional de $\ge 90\%$).
* **Cobertura Global del Proyecto (`app/`):** **94.0%** (supera con creces el umbral constitucional de $\ge 70\%$).
* **Principio de Inversión de Dependencias (DIP):** Aplicado al 100% en `services/` con inyección por parámetro; **0% de uso de `unittest.mock`** en pruebas unitarias de negocio, utilizando exclusivamente el doble de prueba `RepositorioFalsoReservas`.
* **Herramientas MCP Implementadas:** 4 tools completamente funcionales (`crear_reserva`, `listar_reservas`, `consultar_disponibilidad`, `cancelar_reserva`) reutilizando el 100% de la lógica de negocio de `services/`.
* **Seguridad:** Cero secretos en código, autenticación OAuth2 + JWT (HS256), hashing seguro con `bcrypt`, autorización estricta donde `usuario_id` proviene exclusivamente del token JWT verificado (rechazando suplantaciones IDOR/BOLA).

---

## 1. Justificación Arquitectónica (20% - Nivel Excelente)

### 1.1 Estructura en Capas y Responsabilidades
El proyecto está estructurado bajo un patrón de monolito modular con separación estricta de responsabilidades en el directorio `app/`:

```text
app/
├── config.py              <-- Variables de entorno tipadas con pydantic-settings
├── database.py            <-- Sesión SQLAlchemy y motor de base de datos
├── dependencies.py        <-- Inyección de dependencias FastAPI (get_current_user, get_db)
├── models/                <-- Entidades SQLAlchemy ORM exclusivas (Reserva, Usuario)
├── schemas/               <-- Esquemas Pydantic de entrada/salida desacoplados
├── repositories/          <-- Persistencia pura; único componente con acceso a BD
├── services/              <-- Lógica de dominio pura; reglas de negocio y validaciones
├── routers/               <-- Transporte HTTP; mapeo a códigos semánticos REST
├── mcp/
│   ├── server.py          <-- Servidor FastMCP
│   └── tools/             <-- Herramientas MCP que consumen directamente services/
└── utils/                 <-- Funciones puras (hashing bcrypt, firma y decodificación JWT)
```

### 1.2 Justificación en Vivo: ¿Por qué cada regla vive donde vive?
Durante la defensa en vivo, se sustenta la ubicación de cada regla bajo los siguientes fundamentos de ingeniería de software:

1. **Anti-Solapamiento Horario (`services/reservas.py`):**
   * *Por qué vive en `services/`:* La colisión de intervalos horarios ($\max(I_1, I_2) < \min(F_1, F_2)$) es una **regla de negocio pura**, no una regla de transporte HTTP ni una mera restricción de base de datos. Si se colocara en `routers/`, el servidor MCP no podría beneficiarse de ella y duplicaría código o permitiría reservas solapadas. Si se delegara a `repositories/`, se acoplaría la persistencia con lógica algorítmica de dominio.
2. **Bordes Horarios Contiguos Clarificados (`services/reservas.py`):**
   * *Por qué vive en `services/`:* Determinar que una reserva de 10:00 a 11:00 puede coexistir con una de 11:00 a 12:00 es una decisión de dominio aclarada formalmente en `spec.md` vía `/speckit.clarify`. Vive como una función pura auxiliar `_hay_solapamiento()` testeable de forma aislada.
3. **Validación de Fecha Pasada y Coherencia Temporal (`services/reservas.py`):**
   * *Por qué vive en `services/`:* La regla `hora_fin > hora_inicio` y `fecha >= hoy` previene estados inconsistentes del sistema independientemente de si la petición llega por HTTP o por una llamada de función del agente de IA.
4. **Control de Titularidad y Aislamiento (`services/reservas.py`):**
   * *Por qué vive en `services/`:* Comprobar que `reserva.usuario_id == usuario_id` previene vulnerabilidades de autorización horizontal (IDOR/BOLA). Lanza `PermisoDenegadoError`, permitiendo al router traducir la excepción a `HTTP 403 Forbidden` y a MCP retornar `{"error": "No tiene autorización..."}`.
5. **Confirmación de Acción Destructiva en Servidor (`services/reservas.py`):**
   * *Por qué vive en `services/`:* La exigencia de confirmación (`confirmacion=True`) nunca debe confiarse al cliente ni a la "buena voluntad" del LLM. El servidor impone que si `confirmacion is False`, la eliminación se aborta lanzando `AccionNoConfirmadaError` (HTTP 400).

### 1.3 Principio de Inversión de Dependencias (DIP) y Prohibición de Mocks
De acuerdo con el Artículo II.3 de la constitución, ninguna función de negocio importa ni instancia directamente el repositorio. En su lugar, recibe el repositorio por parámetro con un valor por defecto:
```python
def crear_reserva(
    db,
    usuario_id: int,
    espacio: str,
    fecha: date,
    hora_inicio: time,
    hora_fin: time,
    motivo: str = "",
    repo=reservas_repository,  # Inyección por parámetro (DIP)
) -> dict:
```
Esto permite que en las pruebas unitarias (`tests/test_reservas_services.py`) se inyecte `RepositorioFalsoReservas`, eliminando por completo `unittest.mock`. Mockear funciones o clases reintroduce acoplamiento con la implementación interna; DIP prueba el contrato público de forma determinista y ultrarrápida (16 tests en 0.5s).

---

## 2. Seguridad y Gestión de Identidad (20% - Nivel Excelente)

### 2.1 Criptografía y Flujo OAuth2 + JWT
* **Almacenamiento Seguro:** Las contraseñas de los usuarios jamás se persisten en texto claro. Se utiliza el algoritmo `bcrypt` con factores de coste adaptativos gestionados por `passlib[bcrypt]`.
* **Autenticación:** Flujo estándar OAuth2 Password Flow (`POST /usuarios/token`) recibiendo credenciales mediante formulario y emitiendo un JSON Web Token (JWT) firmado con algoritmo simétrico HS256 y expiración temporal (30 minutos por defecto).
* **Gestión de Secretos:** La variable `SECRET_KEY`, el algoritmo y el tiempo de expiración se leen exclusivamente a través de variables de entorno administradas por Pydantic-Settings en `app/config.py`. No existen credenciales quemadas en el código fuente.
* **Archivos `.env` y `.env.example`:** El archivo `.env` real se encuentra formalmente ignorado por Git en `.gitignore`. Se versiona `.env.example` documentando cada clave requerida con valores ficticios y descriptivos.

### 2.2 Identidad Inmutable: Prohibición de `usuario_id` del Cliente
En conformidad con el Artículo IV.3, ningún endpoint de reservas acepta `usuario_id` en el cuerpo JSON ni en los parámetros de consulta. La identidad del usuario se extrae estrictamente mediante la dependencia de FastAPI:
```python
current_user: Usuario = Depends(get_current_user)
```
La función `get_current_user` valida criptográficamente la firma del JWT, decodifica el *subject* (`sub`: email) y recupera la entidad `Usuario`.

### 2.3 Justificación en Vivo: ¿Qué pasaría si un endpoint no verificara el JWT?
Si un endpoint omitiera la verificación del JWT y en su lugar aceptara `usuario_id` provisto por el cliente:
1. **Suplantación de Identidad (Spoofing) y Vulnerabilidad BOLA/IDOR:** Cualquier actor malicioso podría enviar `{"usuario_id": 1}` y consultar, registrar o cancelar las reservas de otro médico, sala ejecutiva o cliente simplemente iterando identificadores numéricos.
2. **Pérdida de No-Repudio y Auditoría:** Los registros de base de datos quedarían viciados, ya que no habría garantía criptográfica de que el usuario que realizó la acción fue quien efectivamente poseía la sesión activa.
3. **Escalamiento Horizontal de Privilegios:** Se rompería el aislamiento constitucional del sistema, exponiendo datos personales y disponibilidad privada de terceros.

---

## 3. Contratos REST y Servidor MCP (25% - Nivel Excelente)

### 3.1 Contrato de la API REST
Todos los endpoints implementan códigos de estado HTTP semánticos y modelos Pydantic diferenciados:

| Método | Ruta | Auth JWT | Payload / Parámetros | Respuesta Éxito | Códigos de Error Controlados |
|---|---|---|---|---|---|
| `POST` | `/usuarios/` | No | `{"email", "password"}` | `201 Created` | `400` (email duplicado), `422` |
| `POST` | `/usuarios/token` | No | Form: `username`, `password` | `200 OK` (token bearer) | `401` (credenciales inválidas) |
| `POST` | `/reservas/` | Sí | `espacio`, `fecha`, `hora_inicio`, `hora_fin`, `motivo` | `201 Created` | `400` (solapamiento/hora inválida), `401`, `422` |
| `GET` | `/reservas/` | Sí | Query: `skip` (0), `limit` (20), `fecha` (opc) | `200 OK` (lista reservas) | `401` (sin token) |
| `GET` | `/reservas/disponibilidad` | Sí | Query: `espacio`, `fecha` | `200 OK` (bloques ocupados) | `400`, `401` |
| `GET` | `/reservas/{id}` | Sí | Path: `id` | `200 OK` (detalle reserva) | `401`, `403` (ajena), `404` (no existe) |
| `DELETE` | `/reservas/{id}` | Sí | Path: `id`, Query: `confirmacion=true` | `204 No Content` | `400` (sin confirmar), `401`, `403`, `404` |

### 3.2 Contrato y Herramientas del Servidor MCP
El servidor MCP (`app/mcp/server.py`) fue construido con **FastMCP** exponiendo 4 herramientas semánticas que reutilizan directamente `services/reservas.py`:

1. **`crear_reserva`:**
   * *Descripción:* Crea una reserva de un espacio compartido validando solapamientos temporales y horarios consistentes.
   * *Entrada:* `espacio: str`, `fecha: str (YYYY-MM-DD)`, `hora_inicio: str (HH:MM)`, `hora_fin: str (HH:MM)`, `motivo: str`, `token: str | None`.
   * *Retorno:* `{"status": "success", "reserva": {...}}` o `{"error": "Conflicto de horario: ..."}`.
2. **`listar_reservas`:**
   * *Descripción:* Lista las reservas asociadas al usuario autenticado con soporte de paginación y filtro por fecha.
   * *Entrada:* `skip: int = 0`, `limit: int = 20`, `fecha: str | None`, `token: str | None`.
   * *Retorno:* `{"total": N, "reservas": [...]}`.
3. **`consultar_disponibilidad`:**
   * *Descripción:* Consulta los intervalos horarios ocupados de un espacio específico para una fecha determinada.
   * *Entrada:* `espacio: str`, `fecha: str`.
   * *Retorno:* `{"espacio": "...", "fecha": "...", "total_ocupado": N, "reservas_ocupadas": [...]}`.
4. **`cancelar_reserva`:**
   * *Descripción:* Cancela una reserva existente exigiendo obligatoriamente `confirmacion=True`.
   * *Entrada:* `reserva_id: int`, `confirmacion: bool = False`, `token: str | None`.
   * *Retorno:* `{"status": "reserva_cancelada", "id": N}` o `{"error": "Acción destructiva no confirmada..."}`.

### 3.3 Consistencia de Errores y Gestión de Identidad en MCP
* **Manejo Estructurado de Errores:** En REST las excepciones de dominio se traducen a códigos HTTP vía `HTTPException`. En MCP, las excepciones se capturan y serializan como diccionarios estructurados `{"error": str(exc)}`. Esto garantiza que los clientes LLM procesen el error como información de contexto sin romper el socket de comunicación.
* **Resolución de Identidad:** Cuando la llamada proviene de un transporte con cabecera de autenticación, la función `resolver_usuario_id()` decodifica el JWT real. Para transportes locales de consola (`stdio`) donde no existe paso de cabeceras HTTP, se cuenta con una simplificación consciente debidamente documentada que recurre al usuario configurado en `DEMO_USER_EMAIL`.

---

## 4. Estrategia y Resultados de Testing (20% - Nivel Excelente)

### 4.1 Pirámide de Pruebas Implementada
Se desarrollaron suites completas en tres niveles:
1. **Pruebas Unitarias de Dominio (`tests/test_reservas_services.py`):** 16 pruebas con `RepositorioFalsoReservas`, validando cada regla de negocio sin dependencias de base de datos ni mocks.
2. **Pruebas de Integración con Base de Datos Real (`tests/test_integracion_reservas.py`):** Pruebas contra una base de datos SQLite real creada en disco temporal, certificando persistencia transaccional y relaciones foráneas.
3. **Pruebas de API REST con `TestClient` (`tests/test_api_reservas.py`):** 11 pruebas de extremo a extremo que prueban el ciclo HTTP completo, generación y validación de tokens JWT, códigos de estado y serialización Pydantic.
4. **Pruebas de Herramientas MCP (`tests/test_mcp_reservas.py`):** 9 pruebas verificando llamadas a las tools, respuestas JSON, captura de errores y confirmación destructiva en servidor.

### 4.2 Matriz de Correspondencia: Regla de Negocio (`spec.md`) $\to$ Prueba Automatizada

| Regla de Negocio en `spec.md` | Caso de Error / Validación | Archivo y Función de Prueba | Resultado |
|---|---|---|---|
| **RN-01 (Anti-Solapamiento)** | Solapamiento total o parcial en el mismo espacio | `tests/test_reservas_services.py::test_rn01_solapamiento_total_rechazado`<br>`tests/test_api_reservas.py::test_crear_reserva_solapamiento_400` | **PASSED** |
| **RN-01b (Borde Exacto)** | Horarios consecutivos contiguos permitidos ($10:00=10:00$) | `tests/test_reservas_services.py::test_rn01b_borde_exacto_permitido`<br>`tests/test_api_reservas.py::test_crear_reserva_borde_exacto_201` | **PASSED** |
| **RN-02 (Coherencia Temporal)** | `hora_fin` anterior o igual a `hora_inicio` | `tests/test_reservas_services.py::test_rn02_hora_fin_menor_o_igual_a_inicio`<br>`tests/test_api_reservas.py::test_crear_reserva_horarios_invalidos_400` | **PASSED** |
| **RN-02b (No Retroactividad)** | Fecha de reserva anterior a la fecha actual | `tests/test_reservas_services.py::test_rn02b_fecha_pasada_rechazada`<br>`tests/test_api_reservas.py::test_crear_reserva_fecha_pasada_400` | **PASSED** |
| **RN-03 (Titularidad y BOLA)** | Intento de cancelar o ver reserva de otro usuario | `tests/test_reservas_services.py::test_rn03_cancelar_reserva_ajena_rechazado`<br>`tests/test_api_reservas.py::test_obtener_reserva_propia_y_ajena_403`<br>`tests/test_api_reservas.py::test_cancelar_reserva_ciclo_completo` | **PASSED** |
| **RN-04 (Acción Destructiva)** | Cancelación sin confirmación de servidor | `tests/test_reservas_services.py::test_rn04_cancelar_sin_confirmacion_rechazado`<br>`tests/test_mcp_reservas.py::test_mcp_cancelar_reserva_sin_confirmacion` | **PASSED** |
| **Caso Error 5 (Inexistencia)** | Cancelación de un ID no registrado en BD | `tests/test_reservas_services.py::test_rn05_cancelar_reserva_inexistente`<br>`tests/test_mcp_reservas.py::test_mcp_cancelar_reserva_inexistente` | **PASSED** |
| **Seguridad JWT** | Petición sin token o con token alterado | `tests/test_api_reservas.py::test_crear_reserva_api_sin_token_401`<br>`tests/test_api_reservas.py::test_crear_reserva_api_token_invalido_401` | **PASSED** |

### 4.3 Reporte Oficial de Cobertura (`pytest --cov=app`)
Ejecución certificada sobre entorno Python 3.13:
```text
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
app\__init__.py                    0      0   100%
app\config.py                     10      0   100%
app\database.py                   14      0   100%
app\dependencies.py               24      0   100%
app\mcp\__init__.py                0      0   100%
app\mcp\tools\__init__.py          0      0   100%
app\mcp\tools\gastos.py           49     11    78%   31-32, 37, 65-66, 87, 103-104, 115-116, 119
app\mcp\tools\reservas.py         78     18    77%   54-55, 92, 105-106, 133-134, 137, 148-149, 171-172, 175, 187-188, 205-206, 209
app\models\__init__.py             4      0   100%
app\models\gasto.py               11      0   100%
app\models\reserva.py             15      0   100%
app\models\usuario.py             10      0   100%
app\repositories\__init__.py       0      0   100%
app\repositories\gastos.py        28      0   100%
app\repositories\reservas.py      32      1    97%   123
app\repositories\usuarios.py      10      0   100%
app\routers\__init__.py            0      0   100%
app\routers\gastos.py             35      2    94%   58-59
app\routers\reservas.py           44      2    95%   97-98
app\routers\usuarios.py           25      0   100%
app\schemas\__init__.py            4      0   100%
app\schemas\gasto.py              20      0   100%
app\schemas\reserva.py            33      1    97%   20
app\schemas\usuario.py            13      0   100%
app\services\__init__.py           0      0   100%
app\services\gastos.py            49      0   100%
app\services\reservas.py          69      0   100%
app\services\usuarios.py          24      0   100%
app\utils\__init__.py              0      0   100%
app\utils\security.py             22      0   100%
------------------------------------------------------------
TOTAL                            623     35    94%
====================== 72 passed, 48 warnings in 17.12s =======================
```
* **Cobertura en `app/services/reservas.py`:** **100%** (Meta constitucional: $\ge 90\%$).
* **Cobertura Global:** **94%** (Meta constitucional: $\ge 70\%$).

---

## 5. Spec-Driven Development y Corrección al Agente (15% - Nivel Excelente)

### 5.1 Los Cuatro Artefactos Encadenados de Spec-Kit
Los artefactos residen en `specs/002-sistema-reservas/` y `.specify/memory/`:
1. **`constitution.md`:** Codifica formalmente los 7 artículos no negociables adaptados al dominio de reservas (Arquitectura, DIP, Multiusuario, Seguridad, REST, MCP, Testing).
2. **`spec.md`:** Especifica las entidades `Usuario` y `Reserva`, las reglas RN-01 a RN-04, la resolución de borde exacto vía `/speckit.clarify`, las tablas de contratos REST/MCP y los casos de error explícitos.
3. **`plan.md`:** Justificación tecnológica y matriz de trazabilidad explícita decisión técnica $\to$ artículo constitucional.
4. **`tasks.md`:** 14 tareas atómicas ordenadas por capas (`models` $\to$ `repositories` $\to$ `services` $\to$ `routers` $\to$ `mcp` $\to$ `tests`) gobernadas por *Definition of Done (DoD)* donde ninguna tarea avanza sin prueba en verde.

### 5.2 Evidencia del Momento Real donde se Corrigió al Agente
Tal como exige la rúbrica para el nivel Excelente, se documenta el momento real durante la auditoría preventiva (`specs/002-sistema-reservas/analysis.md`) en que se corrigió al agente:

* **Desviación Detectada:** Durante el borrador del plan, el agente propuso implementar la eliminación de reservas directamente en `routers/reservas.py`, ejecutando `reserva_repository.eliminar(db, reserva_id)` sin pasar por `services/` y sin validar si la reserva pertenecía al usuario del JWT ni exigir confirmación de servidor.
* **Artículos Violados:**
  * Artículo I.2: Violación de arquitectura en capas (router saltando la capa de servicio).
  * Artículo III.3 y IV.3: Violación de aislamiento multiusuario (vulnerabilidad IDOR/BOLA, permitiendo que cualquier usuario autenticado borrara reservas ajenas).
  * Artículo VI.4: Violación de acción destructiva segura (servidor no exigía confirmación explícita).
* **Intervención y Corrección:** Se rechazó la propuesta del agente, obligándolo a:
  1. Mover la lógica a `services.reservas.cancelar_reserva()` inyectando el repositorio mediante DIP (Art. II.3).
  2. Implementar la validación de propiedad `reserva["usuario_id"] == usuario_id`, arrojando `PermisoDenegadoError` (HTTP 403).
  3. Exigir la bandera `confirmacion: bool = False`, arrojando `AccionNoConfirmadaError` (HTTP 400) si no es `True`.

---

## 6. Guía para la Demostración en Vivo (Sesión 10)

### 6.1 Demostración de la API REST (Swagger UI)
1. **Iniciar el servidor local:**
   ```powershell
   .venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
   ```
2. **Abrir la documentación interactiva:** Navegar a `http://127.0.0.1:8000/docs`.
3. **Probar el flujo de registro y token:**
   * Ejecutar `POST /usuarios/` con email y contraseña.
   * Ejecutar `POST /usuarios/token` para obtener el JWT. Copiar el token y autorizar en el botón "Authorize" de Swagger (`Bearer <token>`).
4. **Probar la regla de anti-solapamiento (RN-01):**
   * Crear reserva para `sala-a` de 10:00 a 11:00 $\to$ `201 Created`.
   * Intentar crear reserva para `sala-a` de 10:30 a 11:30 $\to$ `400 Bad Request` con mensaje de conflicto.
   * Crear reserva contigua de 11:00 a 12:00 $\to$ `201 Created` (demuestra cumplimiento de RN-01b).
5. **Probar la seguridad y confirmación destructiva:**
   * Ejecutar `DELETE /reservas/{id}` sin el parámetro confirmacion $\to$ `400 Bad Request`.
   * Ejecutar `DELETE /reservas/{id}?confirmacion=true` $\to$ `204 No Content`.

### 6.2 Demostración del Servidor MCP con MCP Inspector
1. **Ejecutar MCP Inspector sobre el servidor del proyecto:**
   ```powershell
   npx @modelcontextprotocol/inspector .venv\Scripts\python.exe -m app.mcp.server
   ```
2. **Verificación de Tools disponibles en Inspector:**
   * Se listarán las tools `crear_reserva`, `listar_reservas`, `consultar_disponibilidad`, `cancelar_reserva`.
3. **Ejecución de `consultar_disponibilidad`:**
   * Pasar parámetros: `espacio: "sala-a"`, `fecha: "2026-10-15"`.
   * Verificar respuesta estructurada en formato JSON sin errores.
4. **Ejecución de `crear_reserva`:**
   * Crear un bloque horario y verificar que al intentar duplicar el horario, MCP retorna `{"error": "Conflicto de horario: ..."}` de forma controlada.

### 6.3 Ejecución de Tests y Verificación de Cobertura en Vivo
Ejecutar en la terminal del aula:
```powershell
.venv\Scripts\pytest.exe --cov=app --cov-report=term-missing
```
Señalar al docente que:
* Se ejecutan los 72 tests en verde.
* `app/services/reservas.py` se encuentra al **100% de cobertura**.
* La cobertura total es del **94%**.

---

## 7. Conclusión

El Proyecto Integrador demuestra una apropiación integral de la arquitectura en capas, los principios SOLID (especialmente DIP), las mejores prácticas de seguridad en APIs y el estándar emergente del Model Context Protocol (MCP). La metodología Spec-Driven Development permitió mantener el control riguroso de la IA, transformando la especificación formal en una barrera inviolable de calidad y seguridad de software.
