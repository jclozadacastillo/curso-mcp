# Proyecto: Curso de Backend y MCP en Python para IA Generativa

**Desarrollador:** Juan Carlos Lozada  
**Institución:** Universidad Regional Autónoma de Los Andes (UNIANDES)  
**Departamento:** Desarrollo de Software  

---

## 🛠️ Sesión 1 — Verificación y Preparación del Entorno

```text
                    Verificación del Entorno — Clase 1                         
+-----------------------------------------------------------------------------+
| Componente               | Estado | Detalle                                 |
|--------------------------+--------+-----------------------------------------|
| Python 3.12              |   OK   | 3.12.10                                 |
| uv                       |   OK   | uv 0.12.7 (x86_64-pc-windows-msvc)      |
| Git                      |   OK   | git version 2.53.0                      |
| Docker                   |   OK   | Docker version 29.7.2, build a7dcaa6    |
| .gitignore protege .env  |   OK   | protege .env                            |
+-----------------------------------------------------------------------------+

Entorno listo. Continuamos con la Clase 2.
```

---

## 🧠 Práctica 1 (Sesión 2) — APIs de IA Generativa y Memoria Conversacional

### Criterios de Aceptación Cumplidos:
1. **Llamada formal a Gemini**: Configuración con `system_instruction`, `temperature=0.6` y `max_output_tokens=600` explícitos en `chat_memory.py`.
2. **Memoria Conversacional (8 Turnos)**: El modelo retuvo en el Turno 8 todos los datos del Turno 1 (*Juan Carlos Lozada, UNIANDES, Desarrollo de Software, FastAPI, MCP, PostgreSQL, Redis*).
3. **Justificación de la Estrategia de Memoria (Ventana Deslizante)**:
   * **Control de Costos y Contexto**: Mantiene un límite estricto de los últimos 8 turnos (16 mensajes), garantizando un techo de gasto predecible.
   * **Cero Sobrecosto de LLM**: A diferencia del *Resumen Progresivo*, no gasta llamadas adicionales para resumir texto viejo.
   * **Baja Latencia**: Se procesa en memoria local en tiempo constante sin latencia adicional.
4. **Auditoría de Tokens en Vivo**: Monitoreo de `prompt_token_count`, `candidates_token_count` y `total_token_count` mediante `usage_metadata`.
5. **Detección de Truncamiento**: Verificación automática de `finish_reason == MAX_TOKENS`.
6. **Manejo de Errores Resiliente**: Distinción entre `ClientError` (4xx) y `ServerError` (5xx) / `429 (Resource Exhausted)` con reintentos automáticos y backoff exponencial.
7. **Seguridad Absoluta**: La clave `GEMINI_API_KEY` se carga vía `.env` y está completamente excluida del repositorio por `.gitignore`.

---

### 🚀 Cómo Ejecutar la Práctica

```powershell
uv run python chat_memory.py
```
