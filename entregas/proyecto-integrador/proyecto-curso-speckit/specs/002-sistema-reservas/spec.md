# Especificación Funcional: Sistema de Gestión y Reserva de Espacios
**Feature ID:** `002-sistema-reservas`  
**Estado:** Aprobado  
**Metodología:** Spec-Driven Development (SDD) con Spec-Kit

---

## 1. Descripción del Sistema
Sistema backend monolítico modular con soporte para API REST y servidor Model Context Protocol (MCP) para la gestión y reserva de espacios compartidos (consultorios médicos, salas de reuniones y canchas deportivas). Permite a los usuarios registrarse, autenticarse mediante JWT, programar reservas sin solapamientos horarios, consultar disponibilidad en tiempo real y cancelar reservas con confirmación de servidor bajo aislamiento estricto de identidad.

---

## 2. Entidades del Dominio

### 2.1 `Usuario`
Representa al usuario registrado en el sistema.
* `id`: Entero autoincremental, clave primaria.
* `email`: Cadena única, formato de correo válido.
* `hashed_password`: Cadena hash (bcrypt). Jamás expuesta en respuestas ni serializada en logs.
* `is_active`: Booleano, estado de la cuenta (por defecto `True`).
* `created_at`: Marca de tiempo UTC de registro.

### 2.2 `Reserva`
Representa una reserva de uso de un espacio específico.
* `id`: Entero autoincremental, clave primaria.
* `espacio`: Cadena identificadora del espacio (`sala-a`, `sala-b`, `consultorio-1`, `cancha-tenis`, etc.).
* `fecha`: Fecha de la reserva (`YYYY-MM-DD`).
* `hora_inicio`: Hora de inicio del bloque reservado (`HH:MM`).
* `hora_fin`: Hora de culminación del bloque reservado (`HH:MM`).
* `motivo`: Descripción o propósito de la reserva (opcional o requerida).
* `usuario_id`: Clave foránea que referencia a `Usuario.id`.
* `created_at`: Marca de tiempo UTC de creación.

---

## 3. Reglas de Negocio Explícitas

* **RN-01 (Anti-Solapamiento):** Una reserva no puede solaparse en fecha y rango horario con otra reserva existente para el mismo espacio, sin importar el usuario dueño de la reserva existente.
  * *Fórmula de intersección:* Existe solapamiento entre la reserva existente $(I_e, F_e)$ y la nueva $(I_n, F_n)$ si:
    $$\max(I_e, I_n) < \min(F_e, F_n)$$
  * *Excepción arrojada:* `SolapamientoReservaError`.

* **RN-01b (Borde Exacto - Clarificado):** Si una reserva termina a las 10:00 y otra comienza a las 10:00 en el mismo espacio, **NO** existe solapamiento. Se permite el uso contiguo de espacios.

* **RN-02 (Coherencia Temporal):** `hora_fin` debe ser estrictamente posterior a `hora_inicio`. No se permiten reservas con duración cero o negativa.
  * *Excepción arrojada:* `HorarioInvalidoError`.

* **RN-02b (No Retroactividad):** La fecha de una nueva reserva no puede ser anterior a la fecha actual del servidor.
  * *Excepción arrojada:* `HorarioInvalidoError`.

* **RN-03 (Aislamiento y Titularidad):** Un usuario únicamente puede visualizar sus propias reservas en los listados y solo puede cancelar aquellas de las cuales es propietario legítimo. El intento de manipular o cancelar una reserva ajena es rechazado categóricamente con código de acceso prohibido.
  * *Excepción arrojada:* `PermisoDenegadoError` (mapeado a HTTP 403 en REST).

* **RN-04 (Confirmación de Acción Destructiva en Servidor):** La cancelación o borrado de una reserva es una operación irreversible. El servidor exige una confirmación explícita (`confirmacion: bool = True`) antes de proceder con el borrado. Si no se envía la confirmación, el servidor rechaza la operación sin depender de que el cliente o modelo de IA decida preguntar por su cuenta.
  * *Excepción arrojada:* `AccionNoConfirmadaError` (mapeado a HTTP 400 en REST).

---

## 4. Aclaraciones Formales (`/speckit.clarify`)

1. **¿Dos reservas contiguas en el límite exacto constituyen solapamiento?**
   * *Resolución:* No. Dos reservas se solapan únicamente si comparten un intervalo de tiempo abierto mayor a cero minutos. Los bordes coincidentes ($F_1 = I_2$) son válidos.
2. **¿Existe un rol administrador con privilegios para ver o cancelar reservas ajenas?**
   * *Resolución:* No. Por política constitucional de seguridad y alcance de este módulo, rige el aislamiento horizontal estricto: cada usuario solo ve y gestiona sus propias reservas.
3. **¿Cómo se propagan los errores en MCP?**
   * *Resolución:* Toda excepción de dominio en `services/` es capturada en las herramientas MCP y retornada como diccionario JSON uniforme `{"error": str(e)}`, impidiendo cierres intempestivos del transporte MCP.
4. **¿Cuál es el identificador de usuario en entornos MCP STDIO?**
   * *Resolución:* Si el cliente MCP soporta autenticación mediante JWT (en cabeceras SSE o parámetros), se utiliza el usuario autenticado. En entornos STDIO locales sin transporte HTTP, se utiliza de forma controlada el usuario activo de la sesión con la limitación documentada explícitamente en el código.

---

## 5. Contrato de la API (REST)

| Método | Ruta | Auth | Parámetros / Request | Éxito | Códigos de Error Esperados |
|---|---|---|---|---|---|
| `POST` | `/usuarios/` | No | `email`, `password` | `201 Created` (`UsuarioResponse`) | `400` email duplicado, `422` validación |
| `POST` | `/usuarios/token` | No | `username` (email), `password` (OAuth2 form) | `200 OK` (`Token`) | `401` credenciales inválidas |
| `GET` | `/usuarios/me` | Sí | Bearer JWT | `200 OK` (`UsuarioResponse`) | `401` token ausente o inválido |
| `POST` | `/reservas/` | Sí | `espacio`, `fecha`, `hora_inicio`, `hora_fin`, `motivo` | `201 Created` (`ReservaResponse`) | `400` solapamiento / horario inválido, `401` sin token, `422` formato |
| `GET` | `/reservas/` | Sí | Query: `skip` (0), `limit` (10), `fecha` (opc) | `200 OK` (`list[ReservaResponse]`) | `401` sin token |
| `GET` | `/reservas/disponibilidad` | Sí | Query: `espacio`, `fecha` | `200 OK` (`DisponibilidadResponse`) | `400` espacio/fecha faltante, `401` |
| `GET` | `/reservas/{id}` | Sí | Path: `id` (int) | `200 OK` (`ReservaResponse`) | `401` sin token, `403` no es dueño, `404` no existe |
| `DELETE` | `/reservas/{id}` | Sí | Path: `id`, Query: `confirmacion=true` | `204 No Content` | `400` falta confirmación, `401` sin token, `403` no es dueño, `404` no existe |

---

## 6. Contrato de Herramientas MCP (Model Context Protocol)

1. **`crear_reserva`**
   * *Argumentos:* `espacio` (str), `fecha` (str: YYYY-MM-DD), `hora_inicio` (str: HH:MM), `hora_fin` (str: HH:MM), `motivo` (str, opcional).
   * *Comportamiento:* Llama a `services.reservas.crear_reserva()`.
   * *Retorno:* Diccionario con la reserva creada o `{"error": "..."}`.

2. **`listar_reservas`**
   * *Argumentos:* `skip` (int = 0), `limit` (int = 10).
   * *Comportamiento:* Llama a `services.reservas.listar_reservas()`.
   * *Retorno:* Lista serializada de reservas del usuario.

3. **`consultar_disponibilidad`**
   * *Argumentos:* `espacio` (str), `fecha` (str: YYYY-MM-DD).
   * *Comportamiento:* Llama a `services.reservas.consultar_disponibilidad()`.
   * *Retorno:* Diccionario con el listado de reservas activas para ese espacio/fecha y rangos horarios ocupados.

4. **`cancelar_reserva`**
   * *Argumentos:* `reserva_id` (int), `confirmacion` (bool = False).
   * *Comportamiento:* Exige `confirmacion=True` en servidor. Llama a `services.reservas.cancelar_reserva()`.
   * *Retorno:* `{"status": "reserva_cancelada", "id": reserva_id}` o `{"error": "..."}` si no se confirmó o no existe.

---

## 7. Casos de Error Explícitos que Deben Tener Test Asociado
1. **Caso 1:** Crear una reserva cuyo horario se solapa con una reserva existente en el mismo espacio $\to$ `SolapamientoReservaError` / HTTP `400`.
2. **Caso 2:** Crear una reserva con `hora_fin` anterior o igual a `hora_inicio` $\to$ `HorarioInvalidoError` / HTTP `400`.
3. **Caso 3:** Listar o crear reservas sin cabecera de autorización / token $\to$ HTTP `401 Unauthorized`.
4. **Caso 4:** Cancelar una reserva que pertenece a otro usuario enviando su ID $\to$ `PermisoDenegadoError` / HTTP `403 Forbidden`.
5. **Caso 5:** Cancelar una reserva inexistente $\to$ `ReservaNoEncontradaError` / HTTP `404 Not Found`.
6. **Caso 6:** Cancelar una reserva sin bandera de confirmación del servidor $\to$ `AccionNoConfirmadaError` / HTTP `400 Bad Request`.
