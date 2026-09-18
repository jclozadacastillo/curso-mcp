"""Tests del reto opcional del Paso 4: actualización de categoría y control de dueño."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.repositories import gastos as gastos_repo
from app.repositories import usuarios as usuarios_repo
from app.utils.security import create_access_token


@pytest.fixture
def patch_client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        session = Session()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    db = Session()
    u1 = usuarios_repo.guardar(db, "owner@test.com", "hash1")
    u2 = usuarios_repo.guardar(db, "other@test.com", "hash2")
    gasto = gastos_repo.guardar(db, u1.id, "Internet fibra", 45.0, "otros")
    db.close()

    token_u1 = create_access_token({"sub": "owner@test.com"})
    token_u2 = create_access_token({"sub": "other@test.com"})

    yield client, gasto["id"], token_u1, token_u2

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_duenio_puede_actualizar_categoria(patch_client):
    """Criterio DUEÑO: el dueño del gasto puede cambiar su categoría exitosamente (200 OK)."""
    client, gasto_id, token_u1, _ = patch_client
    headers = {"Authorization": f"Bearer {token_u1}"}

    res = client.patch(
        f"/gastos/{gasto_id}",
        json={"categoria": "entretenimiento"},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json()["categoria"] == "entretenimiento"


def test_usuario_ajeno_recibe_403(patch_client):
    """Criterio DUEÑO: usuario ajeno recibe 403 Forbidden."""
    client, gasto_id, _, token_u2 = patch_client
    headers = {"Authorization": f"Bearer {token_u2}"}

    res = client.patch(
        f"/gastos/{gasto_id}",
        json={"categoria": "comida"},
        headers=headers,
    )
    assert res.status_code == 403
    assert "no tiene autorización" in res.json()["detail"].lower()


def test_categoria_invalida_recibe_400(patch_client):
    """Criterio VALIDACIÓN: categoría fuera de catálogo recibe 400 Bad Request."""
    client, gasto_id, token_u1, _ = patch_client
    headers = {"Authorization": f"Bearer {token_u1}"}

    res = client.patch(
        f"/gastos/{gasto_id}",
        json={"categoria": "cripto"},
        headers=headers,
    )
    assert res.status_code == 400
    assert "inválida" in res.json()["detail"].lower()


def test_gasto_inexistente_recibe_404(patch_client):
    """Gasto no existente recibe 404 Not Found."""
    client, _, token_u1, _ = patch_client
    headers = {"Authorization": f"Bearer {token_u1}"}

    res = client.patch(
        "/gastos/99999",
        json={"categoria": "comida"},
        headers=headers,
    )
    assert res.status_code == 404
