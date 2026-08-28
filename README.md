# curso-mcp

Proyecto del curso **Programación de Backend y MCP en Python para IA Generativa**.

---

## Sesión 1 — Verificación del Entorno

```text
                          Environment check — Class 1                          
+-----------------------------------------------------------------------------+
| Component                | Status  | Detail                                 |
|--------------------------+---------+----------------------------------------|
| Python 3.12              |   OK    | 3.12.10                                |
| uv                       |   OK    | uv 0.12.7 (x86_64-pc-windows-msvc)     |
| Git                      |   OK    | git version 2.53.0                     |
| Docker                   | WARNING | not found (not required yet)           |
| .gitignore protects .env |   OK    | protects .env                          |
+-----------------------------------------------------------------------------+

Environment ready.
```

---

## Sesión 2 — APIs de IA Generativa y Memoria Conversacional

### Criterios de Aceptación Implementados
1. **Llamada explícita al LLM**: Configuración con `system_instruction`, `temperature` (0.7) y `max_output_tokens` (1000).
2. **Memoria Conversacional (8+ turnos)**: El modelo mantiene el hilo y recuerda en el Turno 8 los datos provistos en el Turno 1 (*nombre: Carlos, stack: Python/FastAPI/MCP, ciudad: Cuenca*).
3. **Monitoreo de Tokens**: Registro y cálculo de `prompt_token_count`, `candidates_token_count` y `total_token_count` en cada respuesta mediante `usage_metadata`.
4. **Manejo de Truncamiento**: Verificación de `finish_reason` para advertir en caso de corte por `MAX_TOKENS`.
5. **Manejo Robusto de Errores**:
   * `ClientError` (4xx): Errores de cliente que no se reintentan (salvo 429 Rate Limit).
   * `ServerError` (5xx) y `429 (Resource Exhausted)`: Reintento automático con backoff exponencial.
6. **Seguridad de Credenciales**: Llave `GEMINI_API_KEY` gestionada exclusivamente mediante variables de entorno (`.env`) protegida por `.gitignore`.

---

### Justificación de la Estrategia de Memoria: Ventana Deslizante (Sliding Window)

Para este chatbot se eligió la estrategia de **Ventana Deslizante (Sliding Window)** por las siguientes razones técnicas y arquitectónicas:

1. **Control Determinista del Presupuesto de Tokens**: Al delimitar la memoria a los últimos $N$ turnos ($N=8$, es decir, 16 mensajes), se garantiza un techo máximo predecible de tokens consumidos por llamada, evitando el desbordamiento de la ventana de contexto (*context window blowout*) y el incremento exponencial de costos.
2. **Baja Latencia y Cero Sobrecosto de LLM**: A diferencia del *Resumen Progresivo* (que requiere una llamada adicional al modelo para resumir turnos antiguos, aumentando latencia y facturación), la ventana deslizante se procesa en memoria local en $\mathcal{O}(1)$ tiempo de cómputo sin llamadas intermedias.
3. **Idoneidad para Conversaciones de Asistencia y Tarea Acotada**: En flujos típicos de soporte técnico o asistente interactivo (entre 4 y 15 turnos), la información relevante se concentra en los turnos recientes, haciendo que la ventana deslizante sea la opción con el mejor balance costo/precisión.

---

### Ejecución del Script de Memoria

```powershell
uv run python chat_memory.py
```
