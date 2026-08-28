# Evidencia de Entrega — Práctica 1 / Sesión 2
**Curso:** Programación de Backend y MCP en Python para IA Generativa  
**Estudiante / Ingeniero:** Juan Carlos Lozada  
**Institución:** Universidad Regional Autónoma de Los Andes (UNIANDES)  
**Departamento:** Desarrollo de Software  

---

## 1. Resumen de Ejecución
* **Modelo utilizado:** `gemini-3.1-flash-lite`
* **Estrategia de Memoria:** Ventana Deslizante (8 turnos / 16 mensajes)
* **Parámetros:** Temperatura = 0.6 | Max Output Tokens = 600
* **Total de tokens acumulados:** 9,965 tokens
* **Resultado de Memoria en Turno 8:** Retención y síntesis 100% precisa de los datos de Juan Carlos Lozada, UNIANDES, FastAPI, MCP, PostgreSQL y Redis.

---

## 2. Transcripción de la Conversación de 8 Turnos

### Turno 1
* **Usuario:** Hola, me llamo Juan Carlos Lozada y trabajo en UNIANDES en el Departamento de Desarrollo de Software. Estamos diseñando un servidor MCP y backend en Python con FastAPI para conectar modelos de lenguaje con los sistemas académicos de la universidad. Usaremos PostgreSQL como base de datos institucional y Redis para la persistencia temporal de las sesiones de los usuarios.
* **Asistente:** Estimado Juan Carlos, es un gusto saludarte a ti y al equipo del Departamento de Desarrollo de Software de UNIANDES. La arquitectura que planteas con FastAPI, MCP, PostgreSQL y Redis es sólida y escalable para entornos universitarios.
* **Métricas:** Prompt: 160 | Respuesta: 85 | Total: 245 | Finish: FinishReason.STOP

### Turno 2
* **Usuario:** Para nuestro equipo de desarrollo en UNIANDES, ¿cuáles son las principales ventajas técnicas de estandarizar nuestro proyecto con `uv` en lugar de usar pip y venv tradicionales?
* **Asistente:** Adoptar `uv` representa un salto cualitativo por su velocidad extrema (hasta 10-100x más rápido), gestión determinista de dependencias (`uv.lock`) y administración unificada del runtime de Python (`uv python`).
* **Métricas:** Prompt: 410 | Respuesta: 120 | Total: 530 | Finish: FinishReason.STOP

### Turno 3
* **Usuario:** En un caso de uso universitario, si un docente adjunta un sílabo o reglamento de 25 páginas a la consulta, ¿cómo afecta esto a la ventana de contexto y al presupuesto de tokens de entrada vs salida?
* **Asistente:** Un documento de 25 páginas satura la ventana de contexto e incrementa la latencia (TTFT). La solución óptima es RAG (*Retrieval-Augmented Generation*) con `pgvector` en PostgreSQL.
* **Métricas:** Prompt: 692 | Respuesta: 290 | Total: 982 | Finish: FinishReason.STOP

### Turno 4
* **Usuario:** Explícame en dos oraciones claras por qué las llamadas a la API de LLMs son stateless y por qué necesitamos una capa intermedia con Redis en UNIANDES para mantener la memoria conversacional.
* **Asistente:** Las llamadas a la API de LLMs son stateless porque el modelo procesa cada solicitud de forma aislada sin memoria de interacciones previas. Implementar Redis es indispensable para persistir el historial de sesiones y reconstruir el contexto de forma rápida y escalable.
* **Métricas:** Prompt: 1024 | Respuesta: 92 | Total: 1116 | Finish: FinishReason.STOP

### Turno 5
* **Usuario:** En el SDK de Google GenAI, ¿cuál es la diferencia técnica entre los roles 'user' y 'model', y por qué la `system_instruction` no debe colocarse en la lista de contenidos?
* **Asistente:** El rol `user` representa la entrada del usuario y `model` las respuestas generadas por la IA. La `system_instruction` se define en la configuración como directiva superior para evitar prompt injection y persistir las reglas institucionales.
* **Métricas:** Prompt: 1162 | Respuesta: 193 | Total: 1355 | Finish: FinishReason.STOP

### Turno 6
* **Usuario:** Si durante el período de matrículas universitarias recibimos alta concurrencia y la API de Gemini responde con un error 429 (Resource Exhausted), ¿cómo debe actuar nuestro backend mediante backoff exponencial?
* **Asistente:** El backend debe implementar reintentos con backoff exponencial y jitter mediante librerías como `tenacity`, desincronizando las solicitudes concurrentes para evitar el efecto estampida (*thundering herd*).
* **Métricas:** Prompt: 1401 | Respuesta: 220 | Total: 1621 | Finish: FinishReason.STOP

### Turno 7
* **Usuario:** ¿Por qué es fundamental para la gestión tecnológica de UNIANDES auditar `usage_metadata` (prompt tokens, candidates tokens y total) en cada petición a la API?
* **Asistente:** Es crítico para la contabilidad de costos y presupuestos por departamento, analítica de patrones de uso, optimización de RAG y monitoreo de latencias en producción.
* **Métricas:** Prompt: 1659 | Respuesta: 197 | Total: 1856 | Finish: FinishReason.STOP

### Turno 8 (Comprobación del Recuerdo de Turno 1)
* **Usuario:** Para concluir nuestra sesión de arquitectura: ¿Recuerdas cuál es mi nombre, en qué institución y departamento trabajo, qué tecnología estamos usando para el backend y qué componentes forman nuestra infraestructura?
* **Asistente:** "Estimado Juan Carlos Lozada, para concluir nuestra sesión, confirmo los detalles de tu arquitectura: eres el responsable del proyecto en el **Departamento de Desarrollo de Software de UNIANDES**. Tu stack tecnológico está cimentado sobre **FastAPI** para el backend, utilizando **Python** y el protocolo **MCP** para la integración con modelos de lenguaje. La infraestructura se complementa con **PostgreSQL** (con `pgvector` para RAG) como base de datos institucional, **Redis** para la persistencia de sesiones *stateless*, y la estandarización de todo el entorno de desarrollo mediante **uv**."
* **Métricas:** Prompt: 1895 | Respuesta: 127 | Total: 2022 | Finish: FinishReason.STOP
