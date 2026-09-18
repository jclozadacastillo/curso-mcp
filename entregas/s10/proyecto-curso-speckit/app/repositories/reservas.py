"""Repositorio de reservas con operaciones de persistencia desacopladas (SQLAlchemy)."""

from datetime import date, time
from typing import Optional
from sqlalchemy.orm import Session
from app.models.reserva import Reserva


def guardar(
    db: Session,
    usuario_id: int,
    espacio: str,
    fecha: date,
    hora_inicio: time,
    hora_fin: time,
    motivo: str = "",
) -> dict:
    """Persiste una nueva reserva en la base de datos y retorna su representación en diccionario."""
    reserva = Reserva(
        usuario_id=usuario_id,
        espacio=espacio.strip().lower(),
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        motivo=motivo or "",
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return {
        "id": reserva.id,
        "usuario_id": reserva.usuario_id,
        "espacio": reserva.espacio,
        "fecha": reserva.fecha,
        "hora_inicio": reserva.hora_inicio,
        "hora_fin": reserva.hora_fin,
        "motivo": reserva.motivo,
        "created_at": reserva.created_at,
    }


def listar_por_usuario(
    db: Session,
    usuario_id: int,
    skip: int = 0,
    limit: int = 20,
    fecha: Optional[date] = None,
) -> list[dict]:
    """Retorna la lista de reservas pertenecientes exclusivamente al usuario indicado."""
    query = (
        db.query(Reserva)
        .filter(Reserva.usuario_id == usuario_id)
    )
    if fecha:
        query = query.filter(Reserva.fecha == fecha)
    
    query = query.order_by(Reserva.fecha.asc(), Reserva.hora_inicio.asc()).offset(skip).limit(limit)
    return [
        {
            "id": r.id,
            "usuario_id": r.usuario_id,
            "espacio": r.espacio,
            "fecha": r.fecha,
            "hora_inicio": r.hora_inicio,
            "hora_fin": r.hora_fin,
            "motivo": r.motivo,
            "created_at": r.created_at,
        }
        for r in query.all()
    ]


def obtener_por_espacio_y_fecha(
    db: Session,
    espacio: str,
    fecha: date,
) -> list[dict]:
    """Obtiene todas las reservas existentes para un espacio y fecha específica (para control de solapamiento)."""
    espacio_norm = espacio.strip().lower()
    reservas = (
        db.query(Reserva)
        .filter(Reserva.espacio == espacio_norm)
        .filter(Reserva.fecha == fecha)
        .order_by(Reserva.hora_inicio.asc())
        .all()
    )
    return [
        {
            "id": r.id,
            "usuario_id": r.usuario_id,
            "espacio": r.espacio,
            "fecha": r.fecha,
            "hora_inicio": r.hora_inicio,
            "hora_fin": r.hora_fin,
            "motivo": r.motivo,
            "created_at": r.created_at,
        }
        for r in reservas
    ]


def obtener_por_id(db: Session, reserva_id: int) -> dict | None:
    """Busca una reserva específica por su identificador primario."""
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        return None
    return {
        "id": reserva.id,
        "usuario_id": reserva.usuario_id,
        "espacio": reserva.espacio,
        "fecha": reserva.fecha,
        "hora_inicio": reserva.hora_inicio,
        "hora_fin": reserva.hora_fin,
        "motivo": reserva.motivo,
        "created_at": reserva.created_at,
    }


def eliminar(db: Session, reserva_id: int) -> bool:
    """Elimina la reserva identificada por su ID."""
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        return False
    db.delete(reserva)
    db.commit()
    return True
