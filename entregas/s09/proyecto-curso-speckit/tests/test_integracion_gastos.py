"""Tests de integración contra base de datos real SQLite en memoria (Artículo VII.4)."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.usuario import Usuario
from app.repositories import gastos as gastos_repo
from app.repositories import usuarios as usuarios_repo


@pytest.fixture
def db_session():
    """Crea una base de datos SQLite en memoria aislada para cada test."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()

    # Sembrar un usuario para asociar gastos
    usuario = usuarios_repo.guardar(session, email="usuario1@test.com", hashed_password="fakehash123")
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


def test_guardar_y_listar_gastos_en_db(db_session):
    """Verifica que el repositorio de gastos persista y filtre correctamente en la base de datos."""
    usuario = usuarios_repo.obtener_por_email(db_session, "usuario1@test.com")
    assert usuario is not None

    gasto1 = gastos_repo.guardar(
        db_session,
        usuario_id=usuario.id,
        descripcion="Cena de trabajo",
        monto=45.0,
        categoria="comida",
    )
    gasto2 = gastos_repo.guardar(
        db_session,
        usuario_id=usuario.id,
        descripcion="Gasolina",
        monto=30.0,
        categoria="transporte",
    )

    assert gasto1["id"] is not None
    assert gasto2["id"] is not None

    gastos = gastos_repo.listar(db_session, usuario_id=usuario.id, skip=0, limit=10)
    assert len(gastos) == 2
    assert gastos[0]["descripcion"] == "Cena de trabajo"
    assert gastos[1]["descripcion"] == "Gasolina"


def test_total_por_categoria_en_db(db_session):
    """Verifica la sumatoria acumulada por categoría en SQL real."""
    usuario = usuarios_repo.obtener_por_email(db_session, "usuario1@test.com")

    gastos_repo.guardar(db_session, usuario.id, "Almuerzo 1", 20.0, "comida")
    gastos_repo.guardar(db_session, usuario.id, "Almuerzo 2", 35.0, "comida")
    gastos_repo.guardar(db_session, usuario.id, "Cine", 15.0, "entretenimiento")

    total_comida = gastos_repo.total_por_categoria(db_session, usuario.id, "comida")
    total_entretenimiento = gastos_repo.total_por_categoria(db_session, usuario.id, "entretenimiento")
    total_transporte = gastos_repo.total_por_categoria(db_session, usuario.id, "transporte")

    assert total_comida == 55.0
    assert total_entretenimiento == 15.0
    assert total_transporte == 0.0


def test_aislamiento_entre_usuarios_en_db(db_session):
    """Verifica que ningún query exponga gastos de un usuario a otro."""
    u1 = usuarios_repo.obtener_por_email(db_session, "usuario1@test.com")
    u2 = usuarios_repo.guardar(db_session, "usuario2@test.com", "fakehash456")

    gastos_repo.guardar(db_session, u1.id, "Gasto Privado U1", 50.0, "otros")
    gastos_repo.guardar(db_session, u2.id, "Gasto Privado U2", 80.0, "otros")

    gastos_u1 = gastos_repo.listar(db_session, usuario_id=u1.id)
    gastos_u2 = gastos_repo.listar(db_session, usuario_id=u2.id)

    assert len(gastos_u1) == 1
    assert gastos_u1[0]["descripcion"] == "Gasto Privado U1"

    assert len(gastos_u2) == 1
    assert gastos_u2[0]["descripcion"] == "Gasto Privado U2"
