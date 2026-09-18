"""Servicio de lógica de negocio para la gestión de reservas de espacios.

Cumple estrictamente con los Artículos I, II (SRP y DIP), III (Aislamiento),
IV (Seguridad), V (Semántica) y VI (Servidor MCP y confirmación destructiva)
de la Constitución del Proyecto.
"""

import logging
from datetime import date, time
from typing import Optional
from app.repositories import reservas as reservas_repository

logger = logging.getLogger(__name__)


# =====================================================================
# Excepciones de Dominio (Art. I.2, Art. II.1)
# =====================================================================

class HorarioInvalidoError(Exception):
    """Excepción lanzada cuando los límites horarios o la fecha son inconsistentes."""
    pass


class SolapamientoReservaError(Exception):
    """Excepción lanzada cuando existe conflicto temporal con otra reserva en el mismo espacio."""
    pass


class ReservaNoEncontradaError(Exception):
    """Excepción lanzada cuando la reserva especificada no existe en el sistema."""
    pass


class PermisoDenegadoError(Exception):
    """Excepción lanzada cuando un usuario intenta acceder o modificar una reserva ajena."""
    pass


class AccionNoConfirmadaError(Exception):
    """Excepción lanzada cuando una acción destructiva no cuenta con confirmación del servidor."""
    pass


# =====================================================================
# Validaciones Atómicas (Principio de Responsabilidad Única - SRP)
# =====================================================================

def _validar_espacio(espacio: str) -> str:
    """Valida que el identificador del espacio sea una cadena no vacía."""
    if not espacio or not espacio.strip():
        raise ValueError("El identificador del espacio no puede estar vacío.")
    return espacio.strip().lower()


def _validar_horarios(hora_inicio: time, hora_fin: time) -> None:
    """Valida que la hora de culminación sea estrictamente posterior a la de inicio."""
    if hora_fin <= hora_inicio:
        raise HorarioInvalidoError(
            f"La hora de fin ({hora_fin.strftime('%H:%M')}) debe ser estrictamente posterior "
            f"a la hora de inicio ({hora_inicio.strftime('%H:%M')})."
        )


def _validar_fecha(fecha: date) -> None:
    """Valida que no se intenten programar reservas para fechas pasadas."""
    if fecha < date.today():
        raise HorarioInvalidoError(
            f"La fecha de reserva ({fecha.isoformat()}) no puede ser anterior a la fecha actual."
        )


def _hay_solapamiento(
    inicio_existente: time,
    fin_existente: time,
    nuevo_inicio: time,
    nuevo_fin: time,
) -> bool:
    """Determina si dos intervalos horarios se intersectan en un tiempo mayor a 0 minutos.
    
    Regla clarificada en /speckit.clarify:
    Si una termina a las 10:00 y la otra inicia a las 10:00, NO existe solapamiento.
    """
    inicio_interseccion = max(inicio_existente, nuevo_inicio)
    fin_interseccion = min(fin_existente, nuevo_fin)
    return inicio_interseccion < fin_interseccion


def _validar_solapamiento(
    db,
    espacio: str,
    fecha: date,
    hora_inicio: time,
    hora_fin: time,
    repo=reservas_repository,
) -> None:
    """Verifica si el espacio ya se encuentra ocupado en el rango horario solicitado."""
    reservas_existentes = repo.obtener_por_espacio_y_fecha(db, espacio=espacio, fecha=fecha)
    for r in reservas_existentes:
        if _hay_solapamiento(r["hora_inicio"], r["hora_fin"], hora_inicio, hora_fin):
            h_ini = r["hora_inicio"].strftime("%H:%M") if hasattr(r["hora_inicio"], "strftime") else str(r["hora_inicio"])
            h_fin = r["hora_fin"].strftime("%H:%M") if hasattr(r["hora_fin"], "strftime") else str(r["hora_fin"])
            raise SolapamientoReservaError(
                f"Conflicto de horario: el espacio '{espacio}' ya está reservado de {h_ini} a {h_fin} el {fecha}."
            )


# =====================================================================
# Servicios de Negocio con Inversión de Dependencias (DIP - Art. II.3)
# =====================================================================

def crear_reserva(
    db,
    usuario_id: int,
    espacio: str,
    fecha: date,
    hora_inicio: time,
    hora_fin: time,
    motivo: str = "",
    repo=reservas_repository,
) -> dict:
    """Crea y persiste una nueva reserva tras certificar disponibilidad, horarios y propiedad."""
    espacio_limpio = _validar_espacio(espacio)
    _validar_fecha(fecha)
    _validar_horarios(hora_inicio, hora_fin)
    _validar_solapamiento(
        db,
        espacio=espacio_limpio,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        repo=repo,
    )

    reserva_creada = repo.guardar(
        db=db,
        usuario_id=usuario_id,
        espacio=espacio_limpio,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        motivo=motivo or "",
    )
    logger.info(
        "Reserva creada con éxito: id=%s espacio=%s usuario_id=%s fecha=%s",
        reserva_creada.get("id"),
        espacio_limpio,
        usuario_id,
        fecha,
    )
    return reserva_creada


def listar_reservas(
    db,
    usuario_id: int,
    skip: int = 0,
    limit: int = 20,
    fecha: Optional[date] = None,
    repo=reservas_repository,
) -> list[dict]:
    """Retorna las reservas pertenecientes exclusivamente al usuario autenticado (Art. III.3)."""
    return repo.listar_por_usuario(
        db=db,
        usuario_id=usuario_id,
        skip=skip,
        limit=limit,
        fecha=fecha,
    )


def obtener_reserva(
    db,
    reserva_id: int,
    usuario_id: int,
    repo=reservas_repository,
) -> dict:
    """Obtiene el detalle de una reserva validando existencia y titularidad del usuario."""
    reserva = repo.obtener_por_id(db=db, reserva_id=reserva_id)
    if not reserva:
        raise ReservaNoEncontradaError(f"La reserva con id {reserva_id} no existe.")
    if reserva["usuario_id"] != usuario_id:
        raise PermisoDenegadoError("No tiene autorización para ver una reserva que pertenece a otro usuario.")
    return reserva


def consultar_disponibilidad(
    db,
    espacio: str,
    fecha: date,
    repo=reservas_repository,
) -> dict:
    """Consulta los bloques ocupados para un espacio y fecha específica."""
    espacio_limpio = _validar_espacio(espacio)
    reservas = repo.obtener_por_espacio_y_fecha(db=db, espacio=espacio_limpio, fecha=fecha)
    intervalos = [
        {
            "hora_inicio": r["hora_inicio"],
            "hora_fin": r["hora_fin"],
            "motivo": r.get("motivo", ""),
        }
        for r in reservas
    ]
    return {
        "espacio": espacio_limpio,
        "fecha": fecha,
        "reservas_ocupadas": intervalos,
        "total_ocupado": len(intervalos),
    }


def cancelar_reserva(
    db,
    reserva_id: int,
    usuario_id: int,
    confirmacion: bool = False,
    repo=reservas_repository,
) -> dict:
    """Cancela una reserva previa confirmación de servidor y verificación de titularidad.
    
    Cumple con el Artículo VI.4 (Acciones destructivas confirmadas en servidor) y
    Artículo IV.3 (Autorización y no vulnerabilidad IDOR).
    """
    if not confirmacion:
        raise AccionNoConfirmadaError(
            "Para cancelar una reserva debe confirmar explícitamente la acción con confirmacion=True."
        )

    reserva = repo.obtener_por_id(db=db, reserva_id=reserva_id)
    if not reserva:
        raise ReservaNoEncontradaError(f"La reserva con id {reserva_id} no existe.")
    if reserva["usuario_id"] != usuario_id:
        raise PermisoDenegadoError(
            "No tiene autorización para cancelar una reserva que pertenece a otro usuario."
        )

    repo.eliminar(db=db, reserva_id=reserva_id)
    logger.info("Reserva eliminada con éxito: id=%s usuario_id=%s", reserva_id, usuario_id)
    return {"status": "reserva_cancelada", "id": reserva_id}
