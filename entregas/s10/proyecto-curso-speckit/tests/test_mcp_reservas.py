"""Pruebas de herramientas MCP para Reservas de Espacios.

Verifica:
- Reutilización directa de services/reservas.py (Artículo VI.1)
- Respuestas estructuradas con manejo de errores {"error": "..."} (Artículo VI.2)
- Confirmación destructiva obligatoria de servidor (Artículo VI.4)
- Identidad de usuario por token o fallback controlado (Artículo VI.5)
"""

from datetime import date, timedelta
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.mcp.tools.reservas import (
    crear_reserva_tool,
    listar_reservas_tool,
    consultar_disponibilidad_tool,
    cancelar_reserva_tool,
)
from app.repositories import usuarios as usuarios_repo
from app.utils.security import hash_password, create_access_token


@pytest.fixture
def mcp_db():
    """Configura una base de datos en memoria y genera token para pruebas MCP."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()

    # Usuario de prueba
    usuario = usuarios_repo.guardar(session, "mcp_user@reservas.com", hash_password("pass123"))
    token = create_access_token({"sub": "mcp_user@reservas.com"})

    yield session, token, usuario.id

    session.close()
    Base.metadata.drop_all(bind=engine)


def test_mcp_crear_reserva_exito(mcp_db):
    """Tool crear_reserva registra exitosamente y retorna estructura de éxito."""
    db, token, _ = mcp_db
    fecha = (date.today() + timedelta(days=2)).isoformat()
    resultado = crear_reserva_tool(
        espacio="sala-mcp",
        fecha=fecha,
        hora_inicio="10:00",
        hora_fin="11:00",
        motivo="Sesión con agente",
        token=token,
        db=db,
    )
    assert resultado.get("status") == "success"
    assert resultado["reserva"]["espacio"] == "sala-mcp"
    assert "error" not in resultado


def test_mcp_crear_reserva_error_solapamiento(mcp_db):
    """Tool crear_reserva ante solapamiento retorna diccionario estructurado con error."""
    db, token, _ = mcp_db
    fecha = (date.today() + timedelta(days=2)).isoformat()

    # Primera reserva
    crear_reserva_tool("sala-mcp", fecha, "10:00", "11:00", token=token, db=db)

    # Segunda reserva solapada (10:30 a 11:30)
    resultado = crear_reserva_tool("sala-mcp", fecha, "10:30", "11:30", token=token, db=db)
    assert "error" in resultado
    assert "Conflicto de horario" in resultado["error"]


def test_mcp_crear_reserva_error_horario_invalido(mcp_db):
    """Tool crear_reserva con hora_fin anterior a hora_inicio retorna error sin crash."""
    db, token, _ = mcp_db
    fecha = (date.today() + timedelta(days=2)).isoformat()
    resultado = crear_reserva_tool("sala-mcp", fecha, "12:00", "11:00", token=token, db=db)
    assert "error" in resultado
    assert "posterior" in resultado["error"]


def test_mcp_listar_reservas_tool(mcp_db):
    """Tool listar_reservas retorna colección de reservas serializadas."""
    db, token, _ = mcp_db
    fecha = (date.today() + timedelta(days=3)).isoformat()
    crear_reserva_tool("auditorio", fecha, "08:00", "09:00", token=token, db=db)
    crear_reserva_tool("auditorio", fecha, "09:00", "10:00", token=token, db=db)

    resultado = listar_reservas_tool(token=token, db=db)
    assert "error" not in resultado
    assert resultado["total"] == 2
    assert len(resultado["reservas"]) == 2


def test_mcp_consultar_disponibilidad_tool(mcp_db):
    """Tool consultar_disponibilidad retorna ocupación del espacio consultado."""
    db, token, _ = mcp_db
    fecha = (date.today() + timedelta(days=4)).isoformat()
    crear_reserva_tool("cancha-squash", fecha, "15:00", "16:00", token=token, db=db)

    resultado = consultar_disponibilidad_tool("cancha-squash", fecha, db=db)
    assert resultado["espacio"] == "cancha-squash"
    assert resultado["total_ocupado"] == 1
    assert len(resultado["reservas_ocupadas"]) == 1


def test_mcp_cancelar_reserva_sin_confirmacion(mcp_db):
    """Tool cancelar_reserva sin confirmación del servidor retorna error estructurado."""
    db, token, _ = mcp_db
    fecha = (date.today() + timedelta(days=5)).isoformat()
    res = crear_reserva_tool("sala-x", fecha, "10:00", "11:00", token=token, db=db)
    reserva_id = res["reserva"]["id"]

    # Cancelar sin confirmacion (confirmacion=False)
    resultado = cancelar_reserva_tool(reserva_id=reserva_id, confirmacion=False, token=token, db=db)
    assert "error" in resultado
    assert "confirmacion=True" in resultado["error"] or "confirmar explícitamente" in resultado["error"]


def test_mcp_cancelar_reserva_con_confirmacion(mcp_db):
    """Tool cancelar_reserva con confirmacion=True elimina exitosamente."""
    db, token, _ = mcp_db
    fecha = (date.today() + timedelta(days=5)).isoformat()
    res = crear_reserva_tool("sala-y", fecha, "10:00", "11:00", token=token, db=db)
    reserva_id = res["reserva"]["id"]

    resultado = cancelar_reserva_tool(reserva_id=reserva_id, confirmacion=True, token=token, db=db)
    assert resultado.get("status") == "reserva_cancelada"
    assert resultado.get("id") == reserva_id


def test_mcp_cancelar_reserva_inexistente(mcp_db):
    """Tool cancelar_reserva sobre un id que no existe retorna mensaje de error controlado."""
    db, token, _ = mcp_db
    resultado = cancelar_reserva_tool(reserva_id=9999, confirmacion=True, token=token, db=db)
    assert "error" in resultado
    assert "no existe" in resultado["error"]


def test_mcp_formatos_invalidos_fecha_y_hora(mcp_db):
    """Verifica manejo de cadenas no parseables en fecha y hora."""
    db, token, _ = mcp_db
    # Fecha malformada
    r_fecha = crear_reserva_tool("sala-z", "fecha-invalida", "10:00", "11:00", token=token, db=db)
    assert "error" in r_fecha
    assert "Formato de fecha" in r_fecha["error"]

    # Hora malformada
    r_hora = crear_reserva_tool("sala-z", "2026-10-10", "hora-invalida", "11:00", token=token, db=db)
    assert "error" in r_hora
    assert "Formato de hora" in r_hora["error"]

    # Listar con filtro por fecha
    r_list_fecha = listar_reservas_tool(fecha="2026-10-10", token=token, db=db)
    assert "reservas" in r_list_fecha
