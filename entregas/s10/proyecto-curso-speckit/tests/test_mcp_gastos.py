"""Tests de las herramientas MCP y su manejo estructurado de errores (Artículo VI y VII.6)."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.mcp.tools.gastos import listar_gastos_tool, registrar_gasto_tool
from app.repositories import usuarios as usuarios_repo
from app.utils.security import create_access_token, hash_password


@pytest.fixture
def mcp_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()

    # Crear usuario real
    u = usuarios_repo.guardar(session, "mcp_user@test.com", hash_password("pass123"))
    session.commit()

    token = create_access_token({"sub": "mcp_user@test.com"})

    yield session, token

    session.close()
    Base.metadata.drop_all(bind=engine)


def test_mcp_registrar_gasto_exito(mcp_db):
    """Caso exitoso de registrar_gasto_tool utilizando token verificado (Artículo VI.4)."""
    db, token = mcp_db
    resultado = registrar_gasto_tool(
        descripcion="Libros de IA",
        monto=75.0,
        categoria="entretenimiento",
        token=token,
        db=db,
    )
    assert resultado.get("exito") is True
    gasto = resultado["gasto"]
    assert gasto["descripcion"] == "Libros de IA"
    assert gasto["monto"] == 75.0
    assert gasto["categoria"] == "entretenimiento"


def test_mcp_error_negocio_categoria_invalida(mcp_db):
    """
    Caso de error de negocio en tool MCP:
    Artículo VI.3: devuelve {"error": "..."}, nunca una excepción no controlada.
    """
    db, token = mcp_db
    resultado = registrar_gasto_tool(
        descripcion="Inversión bursátil",
        monto=200.0,
        categoria="bolsa_de_valores",
        token=token,
        db=db,
    )
    assert "error" in resultado
    assert "inválida" in resultado["error"].lower()


def test_mcp_error_negocio_limite_excedido(mcp_db):
    """Caso de error de negocio: Exceder el tope de 500 devuelve estructura de error."""
    db, token = mcp_db
    # Registrar primero un gasto de 450
    registrar_gasto_tool(
        descripcion="Gasto inicial alto",
        monto=450.0,
        categoria="comida",
        token=token,
        db=db,
    )

    # Intentar registrar 100 adicionales en comida (450 + 100 = 550 > 500)
    resultado = registrar_gasto_tool(
        descripcion="Cena costosa",
        monto=100.0,
        categoria="comida",
        token=token,
        db=db,
    )
    assert "error" in resultado
    assert "excede el límite" in resultado["error"].lower()


def test_mcp_fallback_usuario_demo_sin_token(mcp_db):
    """
    Verifica el fallback documentado a usuario demo cuando no se suministra token (stdio).
    Artículo VI.4.
    """
    db, _ = mcp_db
    resultado = registrar_gasto_tool(
        descripcion="Gasto desde stdio",
        monto=15.0,
        categoria="transporte",
        token=None,  # Modo stdio
        db=db,
    )
    assert resultado.get("exito") is True
    assert resultado["gasto"]["descripcion"] == "Gasto desde stdio"


def test_mcp_listar_gastos_tool(mcp_db):
    """Verifica listar_gastos_tool con soporte de paginación."""
    db, token = mcp_db
    registrar_gasto_tool("G1", 10.0, "otros", token=token, db=db)
    registrar_gasto_tool("G2", 20.0, "otros", token=token, db=db)

    resultado = listar_gastos_tool(skip=0, limit=10, token=token, db=db)
    assert resultado.get("exito") is True
    gastos = resultado["gastos"]
    assert len(gastos) == 2
