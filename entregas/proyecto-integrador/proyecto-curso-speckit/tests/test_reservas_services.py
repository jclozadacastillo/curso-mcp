"""Pruebas unitarias de app/services/reservas.py con RepositorioFalso (DIP puro, sin unittest.mock).

Cumple taxativamente con el Artículo II.4 y el Artículo VII.2 de la Constitución:
Cada regla de negocio explícita de spec.md tiene una prueba identificable.
"""

from datetime import date, time, timedelta, datetime
import pytest

from app.services.reservas import (
    crear_reserva,
    listar_reservas,
    obtener_reserva,
    consultar_disponibilidad,
    cancelar_reserva,
    HorarioInvalidoError,
    SolapamientoReservaError,
    ReservaNoEncontradaError,
    PermisoDenegadoError,
    AccionNoConfirmadaError,
)


class RepositorioFalsoReservas:
    """Implementación en memoria para desacoplar las pruebas de la base de datos."""

    def __init__(self):
        self.reservas: list[dict] = []
        self._next_id: int = 1

    def guardar(
        self,
        db,
        usuario_id: int,
        espacio: str,
        fecha: date,
        hora_inicio: time,
        hora_fin: time,
        motivo: str = "",
    ) -> dict:
        reserva = {
            "id": self._next_id,
            "usuario_id": usuario_id,
            "espacio": espacio.strip().lower(),
            "fecha": fecha,
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin,
            "motivo": motivo or "",
            "created_at": datetime.utcnow(),
        }
        self.reservas.append(reserva)
        self._next_id += 1
        return reserva

    def listar_por_usuario(
        self,
        db,
        usuario_id: int,
        skip: int = 0,
        limit: int = 20,
        fecha: date | None = None,
    ) -> list[dict]:
        resultado = [r for r in self.reservas if r["usuario_id"] == usuario_id]
        if fecha:
            resultado = [r for r in resultado if r["fecha"] == fecha]
        return resultado[skip : skip + limit]

    def obtener_por_espacio_y_fecha(
        self,
        db,
        espacio: str,
        fecha: date,
    ) -> list[dict]:
        espacio_norm = espacio.strip().lower()
        return [
            r for r in self.reservas
            if r["espacio"] == espacio_norm and r["fecha"] == fecha
        ]

    def obtener_por_id(self, db, reserva_id: int) -> dict | None:
        for r in self.reservas:
            if r["id"] == reserva_id:
                return r
        return None

    def eliminar(self, db, reserva_id: int) -> bool:
        for idx, r in enumerate(self.reservas):
            if r["id"] == reserva_id:
                del self.reservas[idx]
                return True
        return False


# =====================================================================
# Tests Unitarios de Reglas de Negocio
# =====================================================================

def test_crear_reserva_exitosa():
    repo = RepositorioFalsoReservas()
    fecha_futura = date.today() + timedelta(days=1)
    
    reserva = crear_reserva(
        db=None,
        usuario_id=1,
        espacio="sala-a",
        fecha=fecha_futura,
        hora_inicio=time(9, 0),
        hora_fin=time(10, 0),
        motivo="Reunión de planificación",
        repo=repo,
    )
    assert reserva["id"] == 1
    assert reserva["espacio"] == "sala-a"
    assert reserva["usuario_id"] == 1


def test_rn01_solapamiento_total_rechazado():
    """RN-01: No permitir reservas que se solapan en fecha y horario en el mismo espacio."""
    repo = RepositorioFalsoReservas()
    fecha = date.today() + timedelta(days=2)
    # Reserva existente de 10:00 a 12:00
    repo.guardar(None, usuario_id=1, espacio="sala-a", fecha=fecha, hora_inicio=time(10, 0), hora_fin=time(12, 0))

    # Intento de reservar de 10:30 a 11:30 (dentro del rango existente)
    with pytest.raises(SolapamientoReservaError) as exc_info:
        crear_reserva(
            db=None,
            usuario_id=2,
            espacio="sala-a",
            fecha=fecha,
            hora_inicio=time(10, 30),
            hora_fin=time(11, 30),
            repo=repo,
        )
    assert "Conflicto de horario" in str(exc_info.value)


def test_rn01_solapamiento_parcial_inicio():
    """RN-01: Conflicto cuando la nueva reserva empieza antes pero termina dentro de la existente."""
    repo = RepositorioFalsoReservas()
    fecha = date.today() + timedelta(days=2)
    repo.guardar(None, usuario_id=1, espacio="sala-a", fecha=fecha, hora_inicio=time(10, 0), hora_fin=time(11, 0))

    with pytest.raises(SolapamientoReservaError):
        crear_reserva(
            db=None,
            usuario_id=2,
            espacio="sala-a",
            fecha=fecha,
            hora_inicio=time(9, 30),
            hora_fin=time(10, 30),
            repo=repo,
        )


def test_rn01_solapamiento_parcial_fin():
    """RN-01: Conflicto cuando la nueva reserva empieza dentro de la existente y termina después."""
    repo = RepositorioFalsoReservas()
    fecha = date.today() + timedelta(days=2)
    repo.guardar(None, usuario_id=1, espacio="sala-a", fecha=fecha, hora_inicio=time(10, 0), hora_fin=time(11, 0))

    with pytest.raises(SolapamientoReservaError):
        crear_reserva(
            db=None,
            usuario_id=2,
            espacio="sala-a",
            fecha=fecha,
            hora_inicio=time(10, 30),
            hora_fin=time(11, 30),
            repo=repo,
        )


def test_rn01b_borde_exacto_permitido():
    """RN-01b: Si una termina a las 10:00 y la otra empieza a las 10:00, NO hay solapamiento."""
    repo = RepositorioFalsoReservas()
    fecha = date.today() + timedelta(days=2)
    repo.guardar(None, usuario_id=1, espacio="sala-a", fecha=fecha, hora_inicio=time(9, 0), hora_fin=time(10, 0))

    # Nueva reserva exactamente a partir de las 10:00
    reserva = crear_reserva(
        db=None,
        usuario_id=2,
        espacio="sala-a",
        fecha=fecha,
        hora_inicio=time(10, 0),
        hora_fin=time(11, 0),
        repo=repo,
    )
    assert reserva["id"] == 2

    # Otra reserva antes exactamente terminando a las 09:00
    reserva_previa = crear_reserva(
        db=None,
        usuario_id=3,
        espacio="sala-a",
        fecha=fecha,
        hora_inicio=time(8, 0),
        hora_fin=time(9, 0),
        repo=repo,
    )
    assert reserva_previa["id"] == 3


def test_rn01_diferente_espacio_no_solapa():
    """Reservas en el mismo horario pero en espacios distintos no deben causar conflicto."""
    repo = RepositorioFalsoReservas()
    fecha = date.today() + timedelta(days=2)
    repo.guardar(None, usuario_id=1, espacio="sala-a", fecha=fecha, hora_inicio=time(10, 0), hora_fin=time(11, 0))

    reserva = crear_reserva(
        db=None,
        usuario_id=2,
        espacio="sala-b",
        fecha=fecha,
        hora_inicio=time(10, 0),
        hora_fin=time(11, 0),
        repo=repo,
    )
    assert reserva["espacio"] == "sala-b"


def test_rn02_hora_fin_menor_o_igual_a_inicio():
    """RN-02: hora_fin debe ser estrictamente posterior a hora_inicio."""
    repo = RepositorioFalsoReservas()
    fecha = date.today() + timedelta(days=1)

    # Caso hora_fin == hora_inicio
    with pytest.raises(HorarioInvalidoError):
        crear_reserva(
            db=None,
            usuario_id=1,
            espacio="sala-a",
            fecha=fecha,
            hora_inicio=time(10, 0),
            hora_fin=time(10, 0),
            repo=repo,
        )

    # Caso hora_fin < hora_inicio
    with pytest.raises(HorarioInvalidoError):
        crear_reserva(
            db=None,
            usuario_id=1,
            espacio="sala-a",
            fecha=fecha,
            hora_inicio=time(11, 0),
            hora_fin=time(10, 0),
            repo=repo,
        )


def test_rn02b_fecha_pasada_rechazada():
    """RN-02b: No se permiten fechas de reserva en el pasado."""
    repo = RepositorioFalsoReservas()
    fecha_pasada = date.today() - timedelta(days=1)

    with pytest.raises(HorarioInvalidoError) as exc:
        crear_reserva(
            db=None,
            usuario_id=1,
            espacio="sala-a",
            fecha=fecha_pasada,
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
            repo=repo,
        )
    assert "no puede ser anterior a la fecha actual" in str(exc.value)


def test_rn03_cancelar_reserva_ajena_rechazado():
    """RN-03: Un usuario solo puede cancelar sus propias reservas (HTTP 403 / PermisoDenegadoError)."""
    repo = RepositorioFalsoReservas()
    fecha = date.today() + timedelta(days=3)
    # Reserva creada por el usuario 1
    reserva = repo.guardar(None, usuario_id=1, espacio="consultorio-1", fecha=fecha, hora_inicio=time(9, 0), hora_fin=time(10, 0))

    # El usuario 2 intenta cancelarla
    with pytest.raises(PermisoDenegadoError):
        cancelar_reserva(
            db=None,
            reserva_id=reserva["id"],
            usuario_id=2,
            confirmacion=True,
            repo=repo,
        )


def test_rn04_cancelar_sin_confirmacion_rechazado():
    """RN-04: La acción destructiva exige confirmación explícita del servidor."""
    repo = RepositorioFalsoReservas()
    fecha = date.today() + timedelta(days=3)
    reserva = repo.guardar(None, usuario_id=1, espacio="cancha-1", fecha=fecha, hora_inicio=time(14, 0), hora_fin=time(15, 0))

    # Intento de cancelación sin confirmación (confirmacion=False por defecto)
    with pytest.raises(AccionNoConfirmadaError):
        cancelar_reserva(
            db=None,
            reserva_id=reserva["id"],
            usuario_id=1,
            confirmacion=False,
            repo=repo,
        )


def test_rn05_cancelar_reserva_inexistente():
    """RN-05: Cancelar un ID que no existe lanza ReservaNoEncontradaError (404)."""
    repo = RepositorioFalsoReservas()
    with pytest.raises(ReservaNoEncontradaError):
        cancelar_reserva(
            db=None,
            reserva_id=9999,
            usuario_id=1,
            confirmacion=True,
            repo=repo,
        )


def test_cancelar_reserva_propia_con_confirmacion():
    """Cancelación exitosa por parte del dueño con confirmación."""
    repo = RepositorioFalsoReservas()
    fecha = date.today() + timedelta(days=1)
    reserva = repo.guardar(None, usuario_id=1, espacio="sala-a", fecha=fecha, hora_inicio=time(9, 0), hora_fin=time(10, 0))

    resultado = cancelar_reserva(
        db=None,
        reserva_id=reserva["id"],
        usuario_id=1,
        confirmacion=True,
        repo=repo,
    )
    assert resultado["status"] == "reserva_cancelada"
    assert repo.obtener_por_id(None, reserva["id"]) is None


def test_listar_reservas_aislamiento():
    """Aislamiento multiusuario: un usuario solo lista sus propias reservas."""
    repo = RepositorioFalsoReservas()
    fecha = date.today() + timedelta(days=1)
    repo.guardar(None, usuario_id=1, espacio="sala-a", fecha=fecha, hora_inicio=time(9, 0), hora_fin=time(10, 0))
    repo.guardar(None, usuario_id=2, espacio="sala-b", fecha=fecha, hora_inicio=time(9, 0), hora_fin=time(10, 0))

    mis_reservas = listar_reservas(None, usuario_id=1, repo=repo)
    assert len(mis_reservas) == 1
    assert mis_reservas[0]["usuario_id"] == 1


def test_obtener_reserva_detalle():
    repo = RepositorioFalsoReservas()
    fecha = date.today() + timedelta(days=1)
    res = repo.guardar(None, usuario_id=1, espacio="sala-a", fecha=fecha, hora_inicio=time(9, 0), hora_fin=time(10, 0))

    # Obtener propia
    det = obtener_reserva(None, reserva_id=res["id"], usuario_id=1, repo=repo)
    assert det["id"] == res["id"]

    # Obtener ajena -> PermisoDenegadoError
    with pytest.raises(PermisoDenegadoError):
        obtener_reserva(None, reserva_id=res["id"], usuario_id=2, repo=repo)

    # Obtener inexistente -> ReservaNoEncontradaError
    with pytest.raises(ReservaNoEncontradaError):
        obtener_reserva(None, reserva_id=999, usuario_id=1, repo=repo)


def test_consultar_disponibilidad():
    repo = RepositorioFalsoReservas()
    fecha = date.today() + timedelta(days=1)
    repo.guardar(None, usuario_id=1, espacio="sala-a", fecha=fecha, hora_inicio=time(9, 0), hora_fin=time(10, 0))
    repo.guardar(None, usuario_id=2, espacio="sala-a", fecha=fecha, hora_inicio=time(14, 0), hora_fin=time(15, 0))

    disp = consultar_disponibilidad(None, espacio="sala-a", fecha=fecha, repo=repo)
    assert disp["espacio"] == "sala-a"
    assert disp["total_ocupado"] == 2
    assert len(disp["reservas_ocupadas"]) == 2


def test_espacio_vacio_rechazado():
    repo = RepositorioFalsoReservas()
    fecha = date.today() + timedelta(days=1)
    with pytest.raises(ValueError):
        crear_reserva(
            db=None,
            usuario_id=1,
            espacio="   ",
            fecha=fecha,
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            repo=repo,
        )
