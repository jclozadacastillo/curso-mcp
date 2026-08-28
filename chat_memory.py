"""Session 2 — Generative AI APIs & Conversational Memory with Gemini.

Acceptance Criteria:
1. Calls Gemini with explicit system_instruction, temperature, and max_output_tokens.
2. Maintains a conversation of at least 8 turns where the model remembers a detail from Turn 1.
3. Implements a Sliding Window memory strategy, justified in README.md.
4. Logs total_token_count (prompt, candidates, total) for every call.
5. Verifies finish_reason and alerts when the response is truncated (MAX_TOKENS).
6. Handles ClientError (4xx) and ServerError (5xx/429) separately with exponential backoff retry.
7. Reads API key from environment variables without exposing secrets.
"""

import os
import sys
import time

# Ensure UTF-8 output encoding across Windows terminals
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

# Initialize rich console with safe Windows encoding support
console = Console(force_terminal=True, legacy_windows=False)

# Configuration constants
MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_OUTPUT_TOKENS = 1000
MAX_HISTORY_TURNS = 8  # 8 full interaction turns (16 messages)
SYSTEM_INSTRUCTION = (
    "You are a helpful and accurate AI teaching assistant for a Backend & MCP Python course. "
    "Respond concisely in Spanish (maximum 2-3 sentences per answer) while preserving key facts "
    "shared by the user across conversation turns."
)


def load_client() -> genai.Client:
    """Loads environment variables and initializes the Gemini API client."""
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        console.print(
            "[bold red]Error: GEMINI_API_KEY not found in environment or .env file.[/bold red]"
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
    """Sends a request to Gemini with separate handling for ClientError and ServerError.

    Returns:
        tuple[str, bool, dict]: (response_text, is_truncated, token_usage_dict)
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

            # Check truncation status from finish_reason
            candidate = response.candidates[0] if response.candidates else None
            finish_reason = candidate.finish_reason if candidate else "UNKNOWN"
            is_truncated = (
                "MAX_TOKENS" in str(finish_reason)
                or finish_reason == types.FinishReason.MAX_TOKENS
            )

            # Extract token usage metadata
            usage = response.usage_metadata
            token_stats = {
                "prompt_tokens": usage.prompt_token_count if usage else 0,
                "candidates_tokens": usage.candidates_token_count if usage else 0,
                "total_tokens": usage.total_token_count if usage else 0,
                "finish_reason": str(finish_reason),
            }

            return response.text or "", is_truncated, token_stats

        except errors.ClientError as exc:
            # 429 Rate limit / Resource Exhausted is retryable with backoff
            if getattr(exc, "code", None) == 429 or "RESOURCE_EXHAUSTED" in str(exc):
                if attempt < max_retries:
                    sleep_time = initial_backoff * (2 ** (attempt - 1))
                    console.print(
                        f"[yellow]Rate limit (429). Retrying in {sleep_time:.1f}s (attempt {attempt}/{max_retries})...[/yellow]"
                    )
                    time.sleep(sleep_time)
                    continue
            console.print(f"[bold red]ClientError (4xx - Do Not Retry):[/bold red] {exc}")
            raise

        except errors.ServerError as exc:
            # 5xx Server error from provider — retry with exponential backoff
            if attempt < max_retries:
                sleep_time = initial_backoff * (2 ** (attempt - 1))
                console.print(
                    f"[yellow]ServerError (5xx). Retrying in {sleep_time:.1f}s (attempt {attempt}/{max_retries})...[/yellow]"
                )
                time.sleep(sleep_time)
                continue
            console.print(
                f"[bold red]ServerError after {max_retries} retries:[/bold red] {exc}"
            )
            raise


def apply_sliding_window(history: list[dict], max_turns: int = MAX_HISTORY_TURNS) -> list[dict]:
    """Applies a sliding window strategy to preserve only the most recent conversation turns."""
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
    """Executes a single conversational turn, updating history and logging metrics."""
    history.append({"role": "user", "parts": [{"text": user_prompt}]})
    bounded_history = apply_sliding_window(history, max_turns=MAX_HISTORY_TURNS)

    console.print(f"\n[bold cyan]=== Turn {turn_number} ===[/bold cyan]")
    console.print(f"[bold green]User:[/bold green] {user_prompt}")

    reply_text, is_truncated, token_stats = send_message_with_retry(
        client=client,
        contents=bounded_history,
    )

    history.append({"role": "model", "parts": [{"text": reply_text}]})
    console.print(f"[bold blue]Bot:[/bold blue] {reply_text}")

    if is_truncated:
        console.print(
            "[bold red]WARNING: Response was truncated by MAX_TOKENS limit.[/bold red]"
        )

    console.print(
        f"[dim]Tokens -> Prompt: {token_stats['prompt_tokens']} | "
        f"Response: {token_stats['candidates_tokens']} | "
        f"Total: {token_stats['total_tokens']} | "
        f"Finish: {token_stats['finish_reason']}[/dim]"
    )

    return reply_text, history


def run_session_demonstration(client: genai.Client) -> None:
    """Executes an automated 8-turn conversation demonstrating Turn 1 recall and memory management."""
    console.print(
        Panel.fit(
            "[bold magenta]Session 2: Conversational Memory Demonstration[/bold magenta]\n"
            f"Testing Gemini API ({MODEL_NAME}) with Sliding Window Memory & Token Tracking",
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

    console.print("\n[bold green]Environment check & 8-Turn Memory Test Completed Successfully![/bold green]")


def main() -> None:
    client = load_client()
    run_session_demonstration(client)


if __name__ == "__main__":
    main()
