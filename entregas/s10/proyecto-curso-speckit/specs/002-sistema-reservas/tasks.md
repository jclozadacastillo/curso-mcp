# Lista de Tareas: Sistema de Gestión y Reserva de Espacios
**Feature ID:** `002-sistema-reservas`  
**Metodología:** Spec-Driven Development (SDD) con Spec-Kit  
**Gobernanza:** Definition of Done (DoD) obligatoria por tarea

---

## Fase 1: Entidades, Modelos y Esquemas
- [x] **T01 — Modelo SQLAlchemy de Reserva**
  - *Archivos:* `app/models/reserva.py`, `app/models/__init__.py`
  - *DoD:* Entidad `Reserva` con `id`, `espacio`, `fecha`, `hora_inicio`, `hora_fin`, `motivo`, `usuario_id` (FK) y relación con `Usuario`.
- [x] **T02 — Esquemas Pydantic de Reserva y Disponibilidad**
  - *Archivos:* `app/schemas/reserva.py`, `app/schemas/__init__.py`
  - *DoD:* Esquemas diferenciados `ReservaCreate`, `ReservaResponse`, `DisponibilidadResponse` con validaciones de tipos.

---

## Fase 2: Repositorio y Persistencia (Capa de Acceso a Datos)
- [x] **T03 — Repositorio SQLAlchemy de Reservas**
  - *Archivos:* `app/repositories/reservas.py`, `app/repositories/__init__.py`
  - *DoD:* Métodos `crear`, `obtener_por_id`, `listar_por_usuario`, `obtener_por_espacio_y_fecha`, `eliminar`. Recibe `db: Session` por parámetro. No implementa reglas de negocio.

---

## Fase 3: Capa de Servicios con DIP y Pruebas Unitarias (Lógica de Negocio Pura)
- [x] **T04 — Excepciones de Dominio y Servicio de Reservas con DIP**
  - *Archivos:* `app/services/reservas.py`, `app/services/__init__.py`
  - *DoD:* Implementación de `crear_reserva`, `listar_reservas`, `consultar_disponibilidad`, `cancelar_reserva` recibiendo `repo` inyectado por parámetro con valor por defecto. Excepciones: `HorarioInvalidoError`, `SolapamientoReservaError`, `ReservaNoEncontradaError`, `PermisoDenegadoError`, `AccionNoConfirmadaError`.
- [x] **T05 — Pruebas Unitarias de Servicios con Repositorio Falso (Sin Mocks)**
  - *Archivos:* `tests/test_reservas_services.py`
  - *DoD:* Implementación de `RepositorioFalsoReservas`. Tests para RN-01 (solapamiento), RN-01b (bordes exactos permitidos), RN-02 (`hora_fin <= hora_inicio`), RN-02b (fecha pasada), RN-03 (permiso denegado por ajena), RN-04 (confirmación obligatoria), RN-05 (reserva inexistente). Cobertura de `services/reservas.py` ≥ 95%.

---

## Fase 4: Capa de Transporte HTTP (Routers REST y Seguridad JWT)
- [x] **T06 — Router de Reservas y Mapeo de Excepciones Semánticas**
  - *Archivos:* `app/routers/reservas.py`, `app/routers/__init__.py`, `app/main.py`
  - *DoD:* Endpoints `POST /reservas/` (201), `GET /reservas/` (200), `GET /reservas/disponibilidad` (200), `GET /reservas/{id}` (200), `DELETE /reservas/{id}` (204). Extracción de `usuario_id` exclusivamente desde `get_current_user`.
- [x] **T07 — Pruebas de API REST con TestClient**
  - *Archivos:* `tests/test_api_reservas.py`
  - *DoD:* Pruebas automatizadas de todos los endpoints y códigos HTTP: 201, 200, 204, 400 (solapamiento), 401 (sin token o token inválido), 403 (intento de borrar ajena), 404 (no existe), 422 (formato).

---

## Fase 5: Capa MCP (Protocolo de Contexto de Modelo)
- [x] **T08 — Herramientas MCP Reutilizando Services**
  - *Archivos:* `app/mcp/tools/reservas.py`, `app/mcp/server.py`
  - *DoD:* Tools `crear_reserva`, `listar_reservas`, `consultar_disponibilidad`, `cancelar_reserva`. Reutilizan `services/reservas.py`. Retorno uniforme `{"error": ...}` ante fallos. Confirmación en servidor para cancelación destructiva.
- [x] **T09 — Pruebas Automatizadas de MCP Tools**
  - *Archivos:* `tests/test_mcp_reservas.py`
  - *DoD:* Verificación de llamadas exitosas, errores capturados y confirmación destructiva en MCP.

---

## Fase 6: Pruebas de Integración y Seguridad
- [x] **T10 — Pruebas de Integración contra Base de Datos Real**
  - *Archivos:* `tests/test_integracion_reservas.py`
  - *DoD:* Operaciones transaccionales completas con motor SQLite real y aislamiento de usuario.
- [x] **T11 — Verificación y Certificación de Cobertura Global**
  - *Archivos:* `pyproject.toml`
  - *DoD:* `pytest --cov=app --cov-report=term-missing` superando ≥ 90% en `services/` y ≥ 70% global sin advertencias bloqueantes.

---

## Fase 7: Entregables Finales e Informe
- [x] **T12 — Auditoría Preventiva y Registro de Desviación Corregida**
  - *Archivos:* `specs/002-sistema-reservas/analysis.md`
  - *DoD:* Registro documental del momento donde se previno o corrigió la desviación del agente respecto a la constitución.
- [x] **T13 — Redacción del Informe Formal y Compilación PDF**
  - *Archivos:* `INFORME_PROYECTO_INTEGRADOR.md`, `generar_pdf_proyecto.py`, `INFORME_PROYECTO_INTEGRADOR.pdf`
  - *DoD:* Documento completo según plantilla oficial de CEDIA/UNIANDES con todas las secciones y métricas.
- [x] **T14 — Empaquetado ZIP del Repositorio**
  - *Archivos:* `proyecto-integrador.zip`
  - *DoD:* Archivo zip listo para subir al aula virtual AVAC / Moodle.
