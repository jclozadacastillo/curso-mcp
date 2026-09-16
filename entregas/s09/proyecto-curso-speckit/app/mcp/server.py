"""Servidor MCP montado con FastMCP para exposición de herramientas de gastos."""

from mcp.server.fastmcp import FastMCP
from app.mcp.tools.gastos import registrar_gasto_tool, listar_gastos_tool

mcp_server = FastMCP("GastosServer")


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
