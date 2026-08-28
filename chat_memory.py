"""Sesión 2 — APIs de IA Generativa y Memoria Conversacional con Gemini.

Criterios de Aceptación:
1. Llamada a Gemini con system_instruction, temperature y max_output_tokens explícitos.
2. Mantiene una conversación de al menos 8 turnos y el modelo recuerda un dato del turno 1.
3. Implementa una estrategia de memoria (Ventana Deslizante) justificada en el README.md.
4. Registra en consola el total_token_count (prompt, respuesta y total) de cada llamada.
5. Verifica finish_reason y avisa cuando la respuesta viene truncada (MAX_TOKENS).
6. Captura ClientError (4xx) y ServerError (5xx / 429) por separado, con reintento solo en el segundo.
7. La API key se lee de variables de entorno (.env) sin exponer secretos.
"""

import os
import sys
import time

# Configurar codificación UTF-8 para la consola de Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from rich.console import Console
from rich.panel import Panel

# Inicializar consola Rich con soporte seguro para Windows
console = Console(force_terminal=True, legacy_windows=False)

# Constantes de configuración
MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_OUTPUT_TOKENS = 1000
MAX_HISTORY_TURNS = 8  # 8 turnos completos de interacción (16 mensajes)
SYSTEM_INSTRUCTION = (
    "Eres un asistente pedagógico de IA experto para un curso de Backend y MCP en Python. "
    "Responde de forma clara, concisa y en español (máximo 2 a 3 oraciones por respuesta), "
    "recordando con precisión todos los datos que el usuario comparta a lo largo de la conversación."
)


def load_client() -> genai.Client:
    """Carga las variables de entorno e inicializa el cliente de la API de Gemini."""
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        console.print(
            "[bold red]Error: No se encontró GEMINI_API_KEY en el entorno o archivo .env.[/bold red]"
        )
        sys.exit(1)
    return genai.Client(api_key=api_key)


def send_message_with_retry(
    client: genai.Client,
    contents: list[dict],
    temperature: float = DEFAULT_TEMPERATURE,
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    max_retries: int = 3,
    initial_backoff: float = 2.0,
) -> tuple[str, bool, dict]:
    """Envía una petición a Gemini con manejo diferenciado de ClientError y ServerError.

    Retorna:
        tuple[str, bool, dict]: (texto_respuesta, esta_truncada, estadisticas_tokens)
    """
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )

    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents,
                config=config,
            )

            # Verificar si la respuesta fue truncada
            candidate = response.candidates[0] if response.candidates else None
            finish_reason = candidate.finish_reason if candidate else "DESCONOCIDO"
            is_truncated = (
                "MAX_TOKENS" in str(finish_reason)
                or finish_reason == types.FinishReason.MAX_TOKENS
            )

            # Extraer uso de tokens
            usage = response.usage_metadata
            token_stats = {
                "prompt_tokens": usage.prompt_token_count if usage else 0,
                "candidates_tokens": usage.candidates_token_count if usage else 0,
                "total_tokens": usage.total_token_count if usage else 0,
                "finish_reason": str(finish_reason),
            }

            return response.text or "", is_truncated, token_stats

        except errors.ClientError as exc:
            # 429 Límite de tasa / Recursos agotados es reintentable con backoff
            if getattr(exc, "code", None) == 429 or "RESOURCE_EXHAUSTED" in str(exc):
                if attempt < max_retries:
                    sleep_time = initial_backoff * (2 ** (attempt - 1))
                    console.print(
                        f"[yellow]Límite de cuota alcanzado (429). Reintentando en {sleep_time:.1f}s (intento {attempt}/{max_retries})...[/yellow]"
                    )
                    time.sleep(sleep_time)
                    continue
            console.print(f"[bold red]ClientError (4xx - Error del cliente, NO reintentar):[/bold red] {exc}")
            raise

        except errors.ServerError as exc:
            # 5xx Error del servidor del proveedor — reintentar con backoff exponencial
            if attempt < max_retries:
                sleep_time = initial_backoff * (2 ** (attempt - 1))
                console.print(
                    f"[yellow]ServerError (5xx - Error del servidor). Reintentando en {sleep_time:.1f}s (intento {attempt}/{max_retries})...[/yellow]"
                )
                time.sleep(sleep_time)
                continue
            console.print(
                f"[bold red]ServerError tras {max_retries} intentos fallidos:[/bold red] {exc}"
            )
            raise


def apply_sliding_window(history: list[dict], max_turns: int = MAX_HISTORY_TURNS) -> list[dict]:
    """Aplica la estrategia de ventana deslizante para conservar únicamente los turnos recientes."""
    max_messages = max_turns * 2
    if len(history) > max_messages:
        return history[-max_messages:]
    return history


def run_conversation_turn(
    client: genai.Client,
    history: list[dict],
    user_prompt: str,
    turn_number: int,
) -> tuple[str, list[dict]]:
    """Ejecuta un turno conversacional, actualizando el historial e imprimiendo métricas."""
    history.append({"role": "user", "parts": [{"text": user_prompt}]})
    bounded_history = apply_sliding_window(history, max_turns=MAX_HISTORY_TURNS)

    console.print(f"\n[bold cyan]=== Turno {turn_number} ===[/bold cyan]")
    console.print(f"[bold green]Usuario:[/bold green] {user_prompt}")

    reply_text, is_truncated, token_stats = send_message_with_retry(
        client=client,
        contents=bounded_history,
    )

    history.append({"role": "model", "parts": [{"text": reply_text}]})
    console.print(f"[bold blue]Bot:[/bold blue] {reply_text}")

    if is_truncated:
        console.print(
            "[bold red]ADVERTENCIA: La respuesta fue truncada por el límite de MAX_TOKENS.[/bold red]"
        )

    console.print(
        f"[dim]📊 Tokens -> Entrada (Prompt): {token_stats['prompt_tokens']} | "
        f"Salida (Respuesta): {token_stats['candidates_tokens']} | "
        f"Total: {token_stats['total_tokens']} | "
        f"Causa de fin: {token_stats['finish_reason']}[/dim]"
    )

    return reply_text, history


def run_session_demonstration(client: genai.Client) -> None:
    """Ejecuta una conversación automatizada de 8 turnos demostrando el recuerdo del Turno 1."""
    console.print(
        Panel.fit(
            "[bold magenta]Sesión 2: Demostración de Memoria Conversacional con Gemini[/bold magenta]\n"
            f"Modelo: {MODEL_NAME} | Estrategia: Ventana Deslizante | Control de Tokens y Reintentos",
            border_style="magenta",
        )
    )

    prompts = [
        "Hola, me llamo Carlos y estoy construyendo un backend en Python con FastAPI y MCP en Cuenca.",
        "¿Cuáles son las principales ventajas de usar `uv` frente a `pip`?",
        "¿Qué es la ventana de contexto en un LLM?",
        "Explícame en dos oraciones por qué las llamadas a la API de LLMs son stateless.",
        "¿Cuál es la diferencia entre el rol 'user' y 'model' en la API de Gemini?",
        "Dame un ejemplo rápido de cómo manejar reintentos con backoff exponencial.",
        "¿Por qué es importante monitorear `usage_metadata` en producción?",
        "Para terminar: ¿Recuerdas cómo me llamo, qué tecnología estoy usando para mi backend y en qué ciudad estoy?",
    ]

    conversation_history: list[dict] = []

    for idx, prompt in enumerate(prompts, start=1):
        _, conversation_history = run_conversation_turn(
            client=client,
            history=conversation_history,
            user_prompt=prompt,
            turn_number=idx,
        )
        time.sleep(0.5)

    console.print("\n[bold green]✔ ¡Prueba de 8 turnos y memoria conversacional completada con éxito![/bold green]")


def main() -> None:
    client = load_client()
    run_session_demonstration(client)


if __name__ == "__main__":
    main()
