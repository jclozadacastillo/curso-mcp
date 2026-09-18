# Constitución del Proyecto: Sistema de Gestión y Reserva de Espacios
**Versión:** 2.0  
**Metodología:** Spec-Driven Development (SDD) con Spec-Kit y Google Antigravity (`agy`)  
**Dominio:** Reserva de Espacios Compartidos (Consultorios, Salas, Canchas)

---

## Preámbulo
Esta constitución establece las reglas arquitectónicas, de diseño, de seguridad y de pruebas innegociables para el desarrollo del **Sistema de Gestión y Reserva de Espacios**. Cualquier código producido por un agente de inteligencia artificial o desarrollador humano debe satisfacer sin excepción los artículos aquí codificados.

---

## Artículo I — Arquitectura en Capas y Desacoplamiento Estricto
1. El proyecto seguirá un patrón de monolito modular con separación estricta de responsabilidades bajo el paquete `app/`:
   * `models/`: Definición exclusiva de entidades SQLAlchemy ORM.
   * `schemas/`: Contratos de datos y validación de entrada/salida mediante esquemas Pydantic.
   * `repositories/`: Capa de persistencia. Único lugar autorizado para ejecutar consultas o transacciones sobre base de datos. Recibe la sesión por parámetro.
   * `services/`: Capa de dominio y lógica de negocio pura. No importa SQLAlchemy ni gestiona sesiones de base de datos directamente.
   * `routers/`: Capa de transporte HTTP (FastAPI). Traduce peticiones web, valida tokens y convierte excepciones de dominio en códigos de estado HTTP semánticos. Nunca implementa lógica de negocio.
   * `mcp/`: Servidor y herramientas de Protocolo de Contexto de Modelo (Model Context Protocol).
   * `utils/`: Utilidades transversales y funciones puras sin estado.
2. Está terminantemente prohibido que una capa salte a otra no adyacente (por ejemplo, `routers/` haciendo consultas directas a la base de datos sin pasar por `services/`).

---

## Artículo II — Principios SOLID y Principio de Inversión de Dependencias (DIP)
1. **Responsabilidad Única (SRP):** Cada función de servicio resuelve una única operación de negocio con validaciones atómicas extraídas (`_validar_horarios`, `_validar_solapamiento`).
2. **Abierto / Cerrado (OCP):** Nuevos estados o catálogos de espacios se gestionan mediante constantes o esquemas extensibles sin modificar el núcleo del servicio.
3. **Inversión de Dependencias (DIP):** Las funciones de `services/` reciben el repositorio como parámetro inyectado con un valor por defecto que apunta a la implementación real:
   ```python
   def crear_reserva(..., repo: ReservaRepository = reserva_repository):
   ```
4. **Prohibición de Mocks en Tests Unitarios:** Queda expresamente prohibido el uso de `unittest.mock` o parches en los tests unitarios de `services/`. Al aplicarse DIP, las pruebas unitarias inyectarán obligatoriamente una implementación falsa (`RepositorioFalsoReservas`) en memoria.

---

## Artículo III — Persistencia y Aislamiento Multiusuario
1. La persistencia se gestiona mediante SQLAlchemy ORM compatible con SQLite (desarrollo y memoria) y PostgreSQL.
2. Las claves primarias serán de tipo entero auto-incremental y las fechas/horas se manejarán con tipos nativos (`date`, `time`).
3. **Aislamiento Multiusuario:** Cada modelo con datos vinculados a usuarios incluye obligatoriamente `usuario_id` como clave foránea (FK). Ninguna consulta de datos personales de reservas puede omitir el filtro por `usuario_id`.
4. El repositorio no valida reglas de negocio; únicamente persiste, actualiza, filtra y recupera datos.

---

## Artículo IV — Seguridad No Negociable y Gestión de Secretos
1. **Contraseñas Seguras:** Ninguna contraseña se almacenará o transmitirá en texto plano. Se utilizará hashing criptográfico mediante `passlib[bcrypt]` con `bcrypt < 4.1.0`.
2. **Autenticación Basada en Tokens:** Flujo estándar OAuth2 Password Bearer con JSON Web Tokens (JWT) firmados mediante algoritmo HMAC-SHA256 (HS256) con tiempo de expiración determinado.
3. **Identidad Confiable:** La identidad del usuario (`usuario_id`) se obtiene **exclusivamente** desde el payload validado del JWT decodificado por la dependencia `get_current_user`. Ningún endpoint aceptará `usuario_id` proveniente del cuerpo (`body`) o de parámetros de consulta (`query`) del cliente.
4. **Gestión de Secretos:** Las credenciales y claves criptográficas residen exclusivamente en variables de entorno leídas mediante `pydantic-settings` (`app/config.py`). Queda prohibido escribir secretos en el código fuente.
5. **Control de Versiones de Configuración:** Se mantendrá un archivo `.env.example` versionado con claves documentadas y valores ficticios. El archivo `.env` real jamás se agregará al control de versiones de Git.
6. **Manejo Seguro de Errores:** Errores internos de servidor (500) nunca deben exponer trazas de error (*stack traces*) ni detalles de base de datos al cliente final.

---

## Artículo V — Convenciones y Diseño de la API REST
1. **Códigos de Estado Semánticos:**
   * `201 Created`: Creación exitosa de un recurso con cabecera de ubicación o representación.
   * `200 OK`: Consulta, listado o actualización exitosa.
   * `204 No Content`: Eliminación o cancelación exitosa sin cuerpo de respuesta.
   * `400 Bad Request`: Violación de regla de negocio o formato inválido.
   * `401 Unauthorized`: Token ausente, expirado o con firma criptográfica inválida.
   * `403 Forbidden`: Intento de acceder o cancelar una reserva que pertenece a otro usuario.
   * `404 Not Found`: Recurso no encontrado.
   * `422 Unprocessable Entity`: Error de validación de tipos o campos en Pydantic.
2. **Esquemas Separados:** Se desacoplan estrictamente los esquemas de entrada (`ReservaCreate`) de los de salida (`ReservaResponse`), protegiendo campos internos.
3. **Paginación:** Las rutas de listado implementan paginación obligatoria mediante `skip` (predeterminado 0) y `limit` (predeterminado 10, máximo 100).

---

## Artículo VI — Herramientas MCP (Model Context Protocol)
1. **Reutilización Obligatoria:** Cada herramienta (*tool*) expuesta en el servidor MCP debe llamar directamente a la función correspondiente de `app/services/`. Jamás duplicará lógica de negocio ni accederá a la base de datos de manera directa.
2. **Contratos Estructurados:** Los errores de negocio en MCP se capturan y retornan de forma determinista como estructuras de error legibles:
   ```json
   {"error": "Mensaje explicativo del error de dominio"}
   ```
   para evitar la ruptura abrupta de la sesión del modelo de lenguaje.
3. **Descripciones Semánticas:** Las descripciones de cada herramienta deben ser precisas, no genéricas, detallando tipos de datos esperados y restricciones.
4. **Acciones Destructivas:** Cualquier herramienta con efecto destructivo (por ejemplo, `cancelar_reserva`) debe exigir confirmación explícita gestionada por el servidor (mediante bandera `confirmacion: bool` validada en backend), nunca delegando la seguridad a la prudencia espontánea del LLM.
5. **Gestión de Identidad:** Las herramientas documentan explícitamente el mecanismo de propagación de identidad del usuario autenticado, anotando cualquier limitación en entornos STDIO.

---

## Artículo VII — Estándar de Testing y Cobertura
1. **Pirámide de Pruebas:** Se implementarán pruebas unitarias, de integración y de contrato de API.
2. **Pruebas Unitarias de Servicios:** Cada regla de negocio explícita definida en la especificación debe contar con una prueba unitaria identificable que inyecte `RepositorioFalsoReservas`.
3. **Umbrales Mínimos de Cobertura:**
   * Cobertura en `app/services/`: **≥ 90%** medido con `pytest-cov`.
   * Cobertura Global (`app` excluyendo puntos de entrada omitidos): **≥ 70%**.
4. **Pruebas de Integración con Base de Datos:** Se ejecutará al menos una prueba de integración contra una base de datos SQLite real para certificar transacciones y persistencia ORM.
5. **Pruebas de Seguridad y Autorización:** Se verificarán explícitamente los casos de rechazo por falta de token (401) e intento de acceso o borrado de recursos ajenos (403).

---

## Gobernanza y Control de Desviaciones
1. Esta constitución es la norma suprema del proyecto. Ninguna sugerencia de un modelo de lenguaje o atajo de desarrollo puede contradecir sus artículos.
2. Si durante la implementación surge la necesidad imperativa de desviarse de algún artículo, la desviación debe declararse formalmente y esperar aprobación humana explícita antes de integrarse al código fuente.
