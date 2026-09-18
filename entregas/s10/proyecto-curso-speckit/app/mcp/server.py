"""Servidor MCP montado con FastMCP para exposición de herramientas de gestión de reservas y gastos."""

from mcp.server.fastmcp import FastMCP
from app.mcp.tools.gastos import registrar_gasto_tool, listar_gastos_tool
from app.mcp.tools.reservas import (
    crear_reserva_tool,
    listar_reservas_tool,
    consultar_disponibilidad_tool,
    cancelar_reserva_tool,
)

mcp_server = FastMCP("ServidorIntegradorMCP")


# =====================================================================
# Herramientas de Gestión de Espacios y Reservas (Proyecto Integrador)
# =====================================================================

@mcp_server.tool(
    name="crear_reserva",
    description=(
        "Crea una reserva de un espacio compartido (sala, consultorio, cancha). "
        "Valida que no existan solapamientos temporales con reservas previas en ese espacio, "
        "que la hora_fin sea posterior a hora_inicio y que la fecha no sea pasada."
    ),
)
def crear_reserva_mcp(
    espacio: str,
    fecha: str,
    hora_inicio: str,
    hora_fin: str,
    motivo: str = "",
    token: str | None = None,
) -> dict:
    """Tool MCP para registrar una reserva de espacio."""
    return crear_reserva_tool(
        espacio=espacio,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        motivo=motivo,
        token=token,
    )


@mcp_server.tool(
    name="listar_reservas",
    description=(
        "Lista las reservas pertenecientes al usuario autenticado, con paginación "
        "opcional (skip, limit) y filtro opcional por fecha (YYYY-MM-DD)."
    ),
)
def listar_reservas_mcp(
    skip: int = 0,
    limit: int = 20,
    fecha: str | None = None,
    token: str | None = None,
) -> dict:
    """Tool MCP para listar reservas propias del usuario."""
    return listar_reservas_tool(
        skip=skip,
        limit=limit,
        fecha=fecha,
        token=token,
    )


@mcp_server.tool(
    name="consultar_disponibilidad",
    description=(
        "Consulta la disponibilidad y rangos horarios ocupados de un espacio específico "
        "(ej. 'sala-a', 'consultorio-1') para una fecha determinada (YYYY-MM-DD)."
    ),
)
def consultar_disponibilidad_mcp(
    espacio: str,
    fecha: str,
) -> dict:
    """Tool MCP para consultar disponibilidad de espacios."""
    return consultar_disponibilidad_tool(
        espacio=espacio,
        fecha=fecha,
    )


@mcp_server.tool(
    name="cancelar_reserva",
    description=(
        "Cancela una reserva existente del usuario autenticado. "
        "ACCIÓN DESTRUCTIVA: Requiere obligatoriamente que confirmacion=True para "
        "proceder con la eliminación en el servidor."
    ),
)
def cancelar_reserva_mcp(
    reserva_id: int,
    confirmacion: bool = False,
    token: str | None = None,
) -> dict:
    """Tool MCP para cancelar una reserva con confirmación de servidor."""
    return cancelar_reserva_tool(
        reserva_id=reserva_id,
        confirmacion=confirmacion,
        token=token,
    )


# =====================================================================
# Herramientas de Gastos (Compatibilidad de prácticas previas)
# =====================================================================

@mcp_server.tool(
    name="registrar_gasto",
    description=(
        "Registra un gasto con descripción, monto y categoría, validando el límite "
        "mensual acumulado de 500 por categoría y pertenencia al usuario autenticado."
    ),
)
def registrar_gasto_mcp(
    descripcion: str,
    monto: float,
    categoria: str,
    token: str | None = None,
) -> dict:
    """Tool MCP para registrar un nuevo gasto."""
    return registrar_gasto_tool(descripcion, monto, categoria, token=token)


@mcp_server.tool(
    name="listar_gastos",
    description="Lista los gastos asociados al usuario autenticado con soporte de paginación.",
)
def listar_gastos_mcp(
    skip: int = 0,
    limit: int = 20,
    token: str | None = None,
) -> dict:
    """Tool MCP para listar gastos."""
    return listar_gastos_tool(skip=skip, limit=limit, token=token)


if __name__ == "__main__":
    mcp_server.run(transport="stdio")
