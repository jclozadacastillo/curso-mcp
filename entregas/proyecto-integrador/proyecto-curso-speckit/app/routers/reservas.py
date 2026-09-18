"""Router HTTP para el recurso Reservas de Espacios.

Cumple estrictamente con los Artículos I.1, I.2 (sin lógica de negocio en routers),
IV.3 (usuario_id extraído únicamente del token JWT verificado) y V (convenciones REST).
"""

from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.usuario import Usuario
from app.schemas.reserva import (
    ReservaCreate,
    ReservaResponse,
    DisponibilidadResponse,
)
from app.services import reservas as reservas_service

router = APIRouter(prefix="/reservas", tags=["reservas"])


@router.post(
    "/",
    response_model=ReservaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva reserva de espacio",
)
def crear_reserva(
    datos: ReservaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea una reserva tras validar disponibilidad, horarios y pertenencia al usuario autenticado."""
    try:
        return reservas_service.crear_reserva(
            db=db,
            usuario_id=current_user.id,
            espacio=datos.espacio,
            fecha=datos.fecha,
            hora_inicio=datos.hora_inicio,
            hora_fin=datos.hora_fin,
            motivo=datos.motivo or "",
        )
    except (
        reservas_service.HorarioInvalidoError,
        reservas_service.SolapamientoReservaError,
        ValueError,
    ) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get(
    "/",
    response_model=List[ReservaResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar las reservas del usuario autenticado",
)
def listar_reservas(
    skip: int = Query(0, ge=0, description="Registros a omitir"),
    limit: int = Query(20, ge=1, le=100, description="Máximo número de registros"),
    fecha: Optional[date] = Query(None, description="Filtrar por fecha específica"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Retorna exclusivamente las reservas del usuario autenticado, con paginación."""
    return reservas_service.listar_reservas(
        db=db,
        usuario_id=current_user.id,
        skip=skip,
        limit=limit,
        fecha=fecha,
    )


@router.get(
    "/disponibilidad",
    response_model=DisponibilidadResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar ocupación y disponibilidad de un espacio en una fecha",
)
def consultar_disponibilidad(
    espacio: str = Query(..., min_length=2, description="Identificador del espacio"),
    fecha: date = Query(..., description="Fecha de consulta"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Retorna los intervalos ocupados para un espacio y fecha específica."""
    try:
        return reservas_service.consultar_disponibilidad(
            db=db,
            espacio=espacio,
            fecha=fecha,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get(
    "/{reserva_id}",
    response_model=ReservaResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener detalle de una reserva propia",
)
def obtener_reserva(
    reserva_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Retorna los datos de la reserva si existe y pertenece al usuario autenticado."""
    try:
        return reservas_service.obtener_reserva(
            db=db,
            reserva_id=reserva_id,
            usuario_id=current_user.id,
        )
    except reservas_service.ReservaNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except reservas_service.PermisoDenegadoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


@router.delete(
    "/{reserva_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancelar/Eliminar una reserva propia",
)
def cancelar_reserva(
    reserva_id: int,
    confirmacion: bool = Query(
        False,
        description="Confirmación explícita obligatoria del servidor para acción destructiva",
    ),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Cancela una reserva propia exigiendo confirmación explícita (Art. VI.4)."""
    try:
        reservas_service.cancelar_reserva(
            db=db,
            reserva_id=reserva_id,
            usuario_id=current_user.id,
            confirmacion=confirmacion,
        )
        return None
    except reservas_service.AccionNoConfirmadaError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except reservas_service.ReservaNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except reservas_service.PermisoDenegadoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
