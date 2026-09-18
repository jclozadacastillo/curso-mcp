"""Repositorio de gastos con operaciones de persistencia desacopladas."""

from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.gasto import Gasto


def guardar(db: Session, usuario_id: int, descripcion: str, monto: float, categoria: str) -> dict:
    """Persiste un nuevo gasto en la base de datos y retorna su representación en diccionario."""
    gasto = Gasto(
        usuario_id=usuario_id,
        descripcion=descripcion,
        monto=monto,
        categoria=categoria,
    )
    db.add(gasto)
    db.commit()
    db.refresh(gasto)
    return {
        "id": gasto.id,
        "usuario_id": gasto.usuario_id,
        "descripcion": gasto.descripcion,
        "monto": gasto.monto,
        "categoria": gasto.categoria,
    }


def listar(db: Session, usuario_id: int, skip: int = 0, limit: int = 20) -> list[dict]:
    """Retorna la lista de gastos pertenecientes exclusivamente al usuario indicado."""
    query = (
        db.query(Gasto)
        .filter(Gasto.usuario_id == usuario_id)
        .order_by(Gasto.id.asc())
        .offset(skip)
        .limit(limit)
    )
    return [
        {
            "id": g.id,
            "usuario_id": g.usuario_id,
            "descripcion": g.descripcion,
            "monto": g.monto,
            "categoria": g.categoria,
        }
        for g in query.all()
    ]


def total_por_categoria(db: Session, usuario_id: int, categoria: str) -> float:
    """Calcula la suma acumulada de los gastos de un usuario en una categoría específica."""
    resultado = (
        db.query(func.coalesce(func.sum(Gasto.monto), 0.0))
        .filter(Gasto.usuario_id == usuario_id)
        .filter(Gasto.categoria == categoria)
        .scalar()
    )
    return float(resultado or 0.0)


def obtener_por_id(db: Session, gasto_id: int) -> dict | None:
    """Busca un gasto por su identificador primario."""
    gasto = db.query(Gasto).filter(Gasto.id == gasto_id).first()
    if not gasto:
        return None
    return {
        "id": gasto.id,
        "usuario_id": gasto.usuario_id,
        "descripcion": gasto.descripcion,
        "monto": gasto.monto,
        "categoria": gasto.categoria,
    }


def actualizar_categoria(db: Session, gasto_id: int, nueva_categoria: str) -> dict | None:
    """Actualiza la categoría de un gasto existente."""
    gasto = db.query(Gasto).filter(Gasto.id == gasto_id).first()
    if not gasto:
        return None
    gasto.categoria = nueva_categoria
    db.commit()
    db.refresh(gasto)
    return {
        "id": gasto.id,
        "usuario_id": gasto.usuario_id,
        "descripcion": gasto.descripcion,
        "monto": gasto.monto,
        "categoria": gasto.categoria,
    }
