"""Prueba de integración con base de datos real SQLite para el dominio de Reservas.

Cumple con el Artículo VII.4 de la Constitución:
Al menos una prueba de integración contra base de datos real (no el repositorio falso).
"""

import os
import tempfile
from datetime import date, time, timedelta
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.repositories import reservas as reservas_repo
from app.repositories import usuarios as usuarios_repo
from app.services import reservas as reservas_service
from app.utils.security import hash_password


@pytest.fixture
def real_db_session():
    """Crea una base de datos SQLite real temporal en disco y provee una sesión limpia."""
    db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = db_file.name
    db_file.close()

    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    yield db

    db.close()
    engine.dispose()
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError:
            pass


def test_integracion_flujo_real_reservas(real_db_session):
    """Flujo completo de persistencia real: usuario, reservas, detección de solapamiento y borrado."""
    db = real_db_session

    # 1. Crear usuarios en base de datos real
    u1 = usuarios_repo.guardar(db, "doctor1@clinica.com", hash_password("passDoc123"))
    u2 = usuarios_repo.guardar(db, "doctor2@clinica.com", hash_password("passDoc456"))
    assert u1.id is not None
    assert u2.id is not None

    fecha_consulta = date.today() + timedelta(days=7)

    # 2. Doctor 1 reserva Consultorio 1 de 09:00 a 10:00 usando services/ con repo real
    r1 = reservas_service.crear_reserva(
        db=db,
        usuario_id=u1.id,
        espacio="consultorio-1",
        fecha=fecha_consulta,
        hora_inicio=time(9, 0),
        hora_fin=time(10, 0),
        motivo="Consulta de cardiología",
        repo=reservas_repo,
    )
    assert r1["id"] is not None
    assert r1["espacio"] == "consultorio-1"

    # 3. Doctor 2 intenta reservar el mismo consultorio en horario superpuesto (09:30 a 10:30)
    with pytest.raises(reservas_service.SolapamientoReservaError):
        reservas_service.crear_reserva(
            db=db,
            usuario_id=u2.id,
            espacio="consultorio-1",
            fecha=fecha_consulta,
            hora_inicio=time(9, 30),
            hora_fin=time(10, 30),
            motivo="Consulta de dermatología",
            repo=reservas_repo,
        )

    # 4. Doctor 2 reserva Consultorio 1 en horario contiguo permitido (10:00 a 11:00)
    r2 = reservas_service.crear_reserva(
        db=db,
        usuario_id=u2.id,
        espacio="consultorio-1",
        fecha=fecha_consulta,
        hora_inicio=time(10, 0),
        hora_fin=time(11, 0),
        motivo="Consulta de dermatología",
        repo=reservas_repo,
    )
    assert r2["id"] is not None

    # 5. Doctor 1 consulta disponibilidad
    disp = reservas_service.consultar_disponibilidad(
        db=db,
        espacio="consultorio-1",
        fecha=fecha_consulta,
        repo=reservas_repo,
    )
    assert disp["total_ocupado"] == 2

    # 6. Aislamiento: Doctor 1 solo lista sus propias reservas
    mis_reservas = reservas_service.listar_reservas(
        db=db,
        usuario_id=u1.id,
        repo=reservas_repo,
    )
    assert len(mis_reservas) == 1
    assert mis_reservas[0]["id"] == r1["id"]

    # 7. Doctor 1 cancela su reserva con confirmación
    cancel_res = reservas_service.cancelar_reserva(
        db=db,
        reserva_id=r1["id"],
        usuario_id=u1.id,
        confirmacion=True,
        repo=reservas_repo,
    )
    assert cancel_res["status"] == "reserva_cancelada"

    # 8. Comprobar que en base de datos ya no está disponible la reserva 1
    disp_post = reservas_service.consultar_disponibilidad(
        db=db,
        espacio="consultorio-1",
        fecha=fecha_consulta,
        repo=reservas_repo,
    )
    assert disp_post["total_ocupado"] == 1
