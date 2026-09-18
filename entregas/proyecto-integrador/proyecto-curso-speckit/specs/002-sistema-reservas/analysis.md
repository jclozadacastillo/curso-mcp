# Auditoría Preventiva de Spec-Kit (`/speckit.analyze`) y Control de Desviaciones
**Feature ID:** `002-sistema-reservas`  
**Dominio:** Sistema de Gestión y Reserva de Espacios  
**Evaluación:** Rúbrica Proyecto Integrador — Criterio *Spec-Driven Development* (Nivel Excelente)

---

## 1. Propósito de la Auditoría
La auditoría preventiva analiza la especificación y el plan de implementación frente a los artículos de la `constitution.md` antes de generar el código fuente. Su objetivo es detectar desviaciones tempranas, asunciones silenciosas del modelo de IA o vulnerabilidades de seguridad que costarían horas de refactorización si se detectaran tardíamente en producción.

---

## 2. Momento Real de Corrección al Agente por Desviación de Artículos Constitucionales

Durante la fase de diseño y generación del plan inicial, el agente propuso la siguiente implementación para el borrado/cancelación de reservas:

```python
# PROPUESTA INICIAL DEL AGENTE (DESVIACIÓN CONSTITUCIONAL)
@router.delete("/{reserva_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_reserva(
    reserva_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Desviación 1 (Art. I.2): El router accede directamente al repositorio
    # Desviación 2 (Art. IV.3 y Art. III.3): No verifica si la reserva pertenece a current_user
    # Desviación 3 (Art. VI.4): No exige confirmación en el servidor
    reserva = reserva_repository.obtener_por_id(db, reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="No encontrada")
    reserva_repository.eliminar(db, reserva)
    return None
```

### Análisis de Violaciones Detectadas:
1. **Violación del Artículo I (Arquitectura en Capas):**
   * El router invocaba directamente `reserva_repository` saltándose por completo la capa `services/reservas.py`.
2. **Violación del Artículo III y IV (Aislamiento y Titularidad):**
   * No se validaba que `reserva.usuario_id == current_user.id`. Cualquier usuario autenticado que pasara un ID arbitrario de reserva ajena habría podido cancelarla (vulnerabilidad IDOR / BOLA - Broken Object Level Authorization).
3. **Violación del Artículo VI.4 (Acción Destructiva en Servidor):**
   * La acción destructiva no solicitaba confirmación gestionada por el servidor, asumiendo que el cliente o el modelo de lenguaje "preguntaría antes".

### Corrección Constitucional Aplicada:
Se intervino formalmente al agente obligándolo a acatar los Artículos I, III, IV y VI:
1. Se movió la lógica a `services.reservas.cancelar_reserva()`, inyectando el repositorio mediante DIP (Art. II).
2. Se implementó la verificación estricta de titularidad: si `reserva.usuario_id != usuario_id`, el servicio lanza `PermisoDenegadoError`, que el router traduce a `HTTP 403 Forbidden` (Art. III.3 y Art. IV.3).
3. Se implementó el parámetro obligatorio `confirmacion: bool = False` en el servicio y servidor: si `not confirmacion`, se lanza `AccionNoConfirmadaError`, traducido a `HTTP 400 Bad Request` con mensaje `"Para cancelar una reserva debe confirmar explícitamente la acción"` (Art. VI.4).

---

## 3. Matriz de Cumplimiento Constitucional Preventivo

| Artículo Constitucional | Riesgo Identificado | Solución Formal Implementada |
|---|---|---|
| **Art. I (Capas)** | Riesgo de que routers o MCP tools ejecuten SQL directo. | `routers` y `mcp/tools` únicamente llaman a funciones de `services/`. |
| **Art. II (DIP)** | Riesgo de usar `unittest.mock` para simular persistencia. | Se define `RepositorioFalsoReservas` inyectado por parámetro por defecto. |
| **Art. III (Multiusuario)** | Riesgo de filtrar reservas de otros usuarios al listar. | `listar_reservas` exige y aplica filtro estricto por `usuario_id`. |
| **Art. IV (Seguridad)** | Riesgo de aceptar `usuario_id` en el body o query. | `usuario_id` proviene única y exclusivamente de `get_current_user` (JWT). |
| **Art. V (REST)** | Riesgo de retornar 200 en creaciones o 400 genéricos. | Códigos semánticos: 201 en creación, 204 en cancelación, 403 en acceso ajeno. |
| **Art. VI (MCP)** | Riesgo de que una excepción no controlada rompa la sesión MCP. | Captura de errores de dominio retornando `{"error": str(e)}`. |
| **Art. VII (Testing)** | Riesgo de cobertura insuficiente en reglas de solapamiento. | Tests unitarios para colisiones totales, parciales, bordes exactos y horas invertidas. |
