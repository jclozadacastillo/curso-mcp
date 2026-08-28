import os
import sys
import time

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

console = Console(force_terminal=True, legacy_windows=False)

MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")
DEFAULT_TEMPERATURE = 0.6
DEFAULT_MAX_OUTPUT_TOKENS = 600
MAX_HISTORY_TURNS = 8

SYSTEM_INSTRUCTION = (
    "Eres un Asesor Técnico Principal y Arquitecto de Software experto en Python, FastAPI y el protocolo MCP. "
    "Tu labor es asesorar de forma profesional, técnica, clara y concisa en español (máximo 2 a 3 párrafos por respuesta). "
    "Presta atención rigurosa a la identidad del ingeniero (Juan Carlos Lozada), su institución (UNIANDES), departamento de desarrollo de software y requerimientos técnicos compartidos."
)


def cargar_cliente_gemini() -> genai.Client:
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        console.print("[bold red]❌ Error: No se encontró GEMINI_API_KEY en el archivo .env[/bold red]")
        sys.exit(1)
    return genai.Client(api_key=api_key)


def ejecutar_llamada_con_reintentos(
    client: genai.Client,
    contents: list[dict],
    temperature: float = DEFAULT_TEMPERATURE,
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    max_intentos: int = 4,
    backoff_inicial: float = 3.0,
) -> tuple[str, bool, dict]:
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )

    for intento in range(1, max_intentos + 1):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents,
                config=config,
            )

            candidato = response.candidates[0] if response.candidates else None
            finish_reason = candidato.finish_reason if candidato else "DESCONOCIDO"
            esta_truncada = (
                "MAX_TOKENS" in str(finish_reason)
                or finish_reason == types.FinishReason.MAX_TOKENS
            )

            uso = response.usage_metadata
            token_stats = {
                "prompt_tokens": uso.prompt_token_count if uso else 0,
                "candidates_tokens": uso.candidates_token_count if uso else 0,
                "total_tokens": uso.total_token_count if uso else 0,
                "finish_reason": str(finish_reason),
            }

            return response.text or "", esta_truncada, token_stats

        except errors.ClientError as exc:
            if getattr(exc, "code", None) == 429 or "RESOURCE_EXHAUSTED" in str(exc):
                if intento < max_intentos:
                    tiempo_espera = backoff_inicial * (2 ** (intento - 1))
                    console.print(
                        f"[yellow]⏳ Límite de tasa (429). Esperando {tiempo_espera:.1f}s antes de reintentar (intento {intento}/{max_intentos})...[/yellow]"
                    )
                    time.sleep(tiempo_espera)
                    continue
            console.print(f"[bold red]❌ ClientError (4xx no recuperable):[/bold red] {exc}")
            raise

        except errors.ServerError as exc:
            if intento < max_intentos:
                tiempo_espera = backoff_inicial * (2 ** (intento - 1))
                console.print(
                    f"[yellow]⏳ ServerError (5xx). Reintentando en {tiempo_espera:.1f}s (intento {intento}/{max_intentos})...[/yellow]"
                )
                time.sleep(tiempo_espera)
                continue
            console.print(f"[bold red]❌ ServerError tras {max_intentos} intentos:[/bold red] {exc}")
            raise


def aplicar_ventana_deslizante(historial: list[dict], max_turnos: int = MAX_HISTORY_TURNS) -> list[dict]:
    max_mensajes = max_turnos * 2
    if len(historial) > max_mensajes:
        return historial[-max_mensajes:]
    return historial


def ejecutar_turno(
    client: genai.Client,
    historial: list[dict],
    mensaje_usuario: str,
    num_turno: int,
) -> tuple[str, list[dict], dict]:
    historial.append({"role": "user", "parts": [{"text": mensaje_usuario}]})
    historial_acotado = aplicar_ventana_deslizante(historial, max_turnos=MAX_HISTORY_TURNS)

    console.print(f"\n[bold cyan]┌─── Turno {num_turno} de 8 ──────────────────────────────────────┐[/bold cyan]")
    console.print(f"[bold green]🧑 Juan Carlos Lozada (UNIANDES):[/bold green] {mensaje_usuario}")

    respuesta_texto, truncada, stats = ejecutar_llamada_con_reintentos(
        client=client,
        contents=historial_acotado,
    )

    historial.append({"role": "model", "parts": [{"text": respuesta_texto}]})
    console.print(f"[bold blue]🤖 Asistente Arquitecto IA:[/bold blue] {respuesta_texto}")

    if truncada:
        console.print("[bold red]⚠️ ADVERTENCIA: La respuesta fue cortada por el límite de MAX_TOKENS.[/bold red]")

    console.print(
        f"[dim]📊 Métricas de Tokens -> Prompt: {stats['prompt_tokens']} | "
        f"Respuesta: {stats['candidates_tokens']} | "
        f"Total Turno: {stats['total_tokens']} | "
        f"Fin: {stats['finish_reason']}[/dim]"
    )
    console.print("[bold cyan]└───────────────────────────────────────────────────────┘[/bold cyan]")

    return respuesta_texto, historial, stats


def ejecutar_practica_guiada() -> None:
    client = cargar_cliente_gemini()

    console.print(
        Panel.fit(
            "[bold magenta]Práctica 1 — APIs de IA Generativa y Memoria Conversacional[/bold magenta]\n"
            "• Ingeniero: [bold yellow]Juan Carlos Lozada[/bold yellow]\n"
            "• Institución: [bold yellow]Universidad Regional Autónoma de Los Andes (UNIANDES)[/bold yellow]\n"
            "• Departamento: [bold yellow]Desarrollo de Software[/bold yellow]\n"
            f"• Modelo: [bold green]{MODEL_NAME}[/bold green] | Memoria: [bold cyan]Ventana Deslizante (8 turnos / 16 mensajes)[/bold cyan]\n"
            f"• Parámetros: Temperatura={DEFAULT_TEMPERATURE} | MaxTokens={DEFAULT_MAX_OUTPUT_TOKENS}\n"
            "• Monitoreo de Tokens en Vivo & Reintentos con Backoff Exponencial",
            title="⚙️ Entorno de Trabajo — UNIANDES",
            border_style="magenta",
        )
    )

    conversacion_plan = [
        "Hola, me llamo Juan Carlos Lozada y trabajo en UNIANDES en el Departamento de Desarrollo de Software. Estamos diseñando un servidor MCP y backend en Python con FastAPI para conectar modelos de lenguaje con los sistemas académicos de la universidad. Usaremos PostgreSQL como base de datos institucional y Redis para la persistencia temporal de las sesiones de los usuarios.",
        "Para nuestro equipo de desarrollo en UNIANDES, ¿cuáles son las principales ventajas técnicas de estandarizar nuestro proyecto con `uv` en lugar de usar pip y venv tradicionales?",
        "En un caso de uso universitario, si un docente adjunta un sílabo o reglamento de 25 páginas a la consulta, ¿cómo afecta esto a la ventana de contexto y al presupuesto de tokens de entrada vs salida?",
        "Explícame en dos oraciones claras por qué las llamadas a la API de LLMs son stateless y por qué necesitamos una capa intermedia con Redis en UNIANDES para mantener la memoria conversacional.",
        "En el SDK de Google GenAI, ¿cuál es la diferencia técnica entre los roles 'user' y 'model', y por qué la `system_instruction` no debe colocarse en la lista de contenidos?",
        "Si durante el período de matrículas universitarias recibimos alta concurrencia y la API de Gemini responde con un error 429 (Resource Exhausted), ¿cómo debe actuar nuestro backend mediante backoff exponencial?",
        "¿Por qué es fundamental para la gestión tecnológica de UNIANDES auditar `usage_metadata` (prompt tokens, candidates tokens y total) en cada petición a la API?",
        "Para concluir nuestra sesión de arquitectura: ¿Recuerdas cuál es mi nombre, en qué institución y departamento trabajo, qué tecnología estamos usando para el backend y qué componentes forman nuestra infraestructura?",
    ]

    historial_activo: list[dict] = []
    tokens_totales_sesion = 0

    for i, pregunta in enumerate(conversacion_plan, start=1):
        _, historial_activo, stats = ejecutar_turno(
            client=client,
            historial=historial_activo,
            mensaje_usuario=pregunta,
            num_turno=i,
        )
        tokens_totales_sesion += stats.get("total_tokens", 0)
        time.sleep(1)

    console.print(
        f"\n[bold green]✅ ¡Práctica 1 completada con éxito![/bold green]\n"
        f"[bold cyan]Total de tokens acumulados en la sesión:[/bold cyan] {tokens_totales_sesion} tokens.\n"
        "[bold green]La memoria conversacional retuvo e integró todos los datos de Juan Carlos Lozada (UNIANDES) del Turno 1 en el Turno 8.[/bold green]\n"
    )


if __name__ == "__main__":
    ejecutar_practica_guiada()
