"""Herramientas MCP para la gestión y reserva de espacios.

Cumple estrictamente con el Artículo VI de la Constitución:
- Reutiliza directamente services/reservas.py sin duplicar lógica.
- Manejo estructurado de errores con retorno consistente {"error": "..."}.
- Confirmación explícita en servidor para acciones destructivas (cancelar_reserva).
- Resolución de identidad vía JWT o fallback documentado para stdio.
"""

from datetime import datetime, date, time
from typing import Optional
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.mcp.tools.gastos import resolver_usuario_id
from app.services import reservas as reservas_service


def _parsear_fecha(fecha_str: str) -> date:
    """Convierte cadena YYYY-MM-DD a objeto date."""
    try:
        return datetime.strptime(fecha_str.strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Formato de fecha inválido '{fecha_str}'. Utilice YYYY-MM-DD.")


def _parsear_hora(hora_str: str) -> time:
    """Convierte cadena HH:MM o HH:MM:SS a objeto time."""
    hora_str = hora_str.strip()
    formatos = ["%H:%M", "%H:%M:%S"]
    for fmt in formatos:
        try:
            return datetime.strptime(hora_str, fmt).time()
        except ValueError:
            continue
    raise ValueError(f"Formato de hora inválido '{hora_str}'. Utilice HH:MM (ej. 10:30).")


def crear_reserva_tool(
    espacio: str,
    fecha: str,
    hora_inicio: str,
    hora_fin: str,
    motivo: str = "",
    token: Optional[str] = None,
    db: Optional[Session] = None,
) -> dict:
    """Crea una reserva de espacio validando solapamientos temporales y horarios.
    
    Reutiliza directamente services.reservas.crear_reserva() (Artículo VI.1).
    """
    sesion_propia = False
    if db is None:
        db = SessionLocal()
        sesion_propia = True

    try:
        usuario_id = resolver_usuario_id(db, token=token)
        fecha_obj = _parsear_fecha(fecha)
        hora_ini_obj = _parsear_hora(hora_inicio)
        hora_fin_obj = _parsear_hora(hora_fin)

        resultado = reservas_service.crear_reserva(
            db=db,
            usuario_id=usuario_id,
            espacio=espacio,
            fecha=fecha_obj,
            hora_inicio=hora_ini_obj,
            hora_fin=hora_fin_obj,
            motivo=motivo or "",
        )
        return {
            "status": "success",
            "reserva": {
                "id": resultado["id"],
                "espacio": resultado["espacio"],
                "fecha": resultado["fecha"].isoformat(),
                "hora_inicio": resultado["hora_inicio"].strftime("%H:%M"),
                "hora_fin": resultado["hora_fin"].strftime("%H:%M"),
                "motivo": resultado["motivo"],
                "usuario_id": resultado["usuario_id"],
            },
        }
    except (
        reservas_service.HorarioInvalidoError,
        reservas_service.SolapamientoReservaError,
        ValueError,
    ) as exc:
        return {"error": str(exc)}
    finally:
        if sesion_propia:
            db.close()


def listar_reservas_tool(
    skip: int = 0,
    limit: int = 20,
    fecha: Optional[str] = None,
    token: Optional[str] = None,
    db: Optional[Session] = None,
) -> dict:
    """Lista las reservas asociadas al usuario autenticado (Artículo VI.1)."""
    sesion_propia = False
    if db is None:
        db = SessionLocal()
        sesion_propia = True

    try:
        usuario_id = resolver_usuario_id(db, token=token)
        fecha_obj = _parsear_fecha(fecha) if fecha else None

        reservas = reservas_service.listar_reservas(
            db=db,
            usuario_id=usuario_id,
            skip=skip,
            limit=limit,
            fecha=fecha_obj,
        )
        return {
            "total": len(reservas),
            "reservas": [
                {
                    "id": r["id"],
                    "espacio": r["espacio"],
                    "fecha": r["fecha"].isoformat(),
                    "hora_inicio": r["hora_inicio"].strftime("%H:%M"),
                    "hora_fin": r["hora_fin"].strftime("%H:%M"),
                    "motivo": r["motivo"],
                }
                for r in reservas
            ],
        }
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        if sesion_propia:
            db.close()


def consultar_disponibilidad_tool(
    espacio: str,
    fecha: str,
    db: Optional[Session] = None,
) -> dict:
    """Consulta los rangos horarios ocupados para un espacio y fecha específica."""
    sesion_propia = False
    if db is None:
        db = SessionLocal()
        sesion_propia = True

    try:
        fecha_obj = _parsear_fecha(fecha)
        disp = reservas_service.consultar_disponibilidad(
            db=db,
            espacio=espacio,
            fecha=fecha_obj,
        )
        return {
            "espacio": disp["espacio"],
            "fecha": disp["fecha"].isoformat(),
            "total_ocupado": disp["total_ocupado"],
            "reservas_ocupadas": [
                {
                    "hora_inicio": r["hora_inicio"].strftime("%H:%M"),
                    "hora_fin": r["hora_fin"].strftime("%H:%M"),
                    "motivo": r.get("motivo", ""),
                }
                for r in disp["reservas_ocupadas"]
            ],
        }
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        if sesion_propia:
            db.close()


def cancelar_reserva_tool(
    reserva_id: int,
    confirmacion: bool = False,
    token: Optional[str] = None,
    db: Optional[Session] = None,
) -> dict:
    """Cancela una reserva propia exigiendo confirmación de servidor (Artículo VI.4)."""
    sesion_propia = False
    if db is None:
        db = SessionLocal()
        sesion_propia = True

    try:
        usuario_id = resolver_usuario_id(db, token=token)
        resultado = reservas_service.cancelar_reserva(
            db=db,
            reserva_id=reserva_id,
            usuario_id=usuario_id,
            confirmacion=confirmacion,
        )
        return resultado
    except (
        reservas_service.AccionNoConfirmadaError,
        reservas_service.ReservaNoEncontradaError,
        reservas_service.PermisoDenegadoError,
    ) as exc:
        return {"error": str(exc)}
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        if sesion_propia:
            db.close()
