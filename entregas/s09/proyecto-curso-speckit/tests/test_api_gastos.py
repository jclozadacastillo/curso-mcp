"""Tests de la API REST de gastos con TestClient y dependency_overrides (Artículo VII.5 y VIII.1)."""

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.dependencies import get_current_user, get_gastos_repo
from app.main import app
from app.models.usuario import Usuario
from tests.test_gastos import RepositorioFalso


@pytest.fixture
def client_y_repo():
    """Configura el TestClient con overrides limpios para cada test."""
    repo = RepositorioFalso()
    usuario_mock = Usuario(id=1, email="test@ejemplo.com", hashed_password="fakehashbcrypt")

    app.dependency_overrides[get_gastos_repo] = lambda: repo
    app.dependency_overrides[get_current_user] = lambda: usuario_mock
    app.dependency_overrides[get_db] = lambda: None

    client = TestClient(app)
    yield client, repo

    app.dependency_overrides.clear()


def test_crear_gasto_api_exito(client_y_repo):
    """POST /gastos/ retorna 201 y la estructura del gasto creado."""
    client, repo = client_y_repo
    payload = {
        "descripcion": "Desayuno de trabajo",
        "monto": 12.50,
        "categoria": "comida",
    }
    response = client.post("/gastos/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["descripcion"] == "Desayuno de trabajo"
    assert data["monto"] == 12.50
    assert data["categoria"] == "comida"
    assert data["usuario_id"] == 1


def test_crear_gasto_categoria_invalida_api(client_y_repo):
    """POST /gastos/ con categoría fuera del catálogo retorna 400 Bad Request."""
    client, _ = client_y_repo
    payload = {
        "descripcion": "Inversión cripto",
        "monto": 100.0,
        "categoria": "criptomonedas",
    }
    response = client.post("/gastos/", json=payload)
    assert response.status_code == 400
    assert "inválida" in response.json()["detail"].lower()


def test_crear_gasto_limite_excedido_api(client_y_repo):
    """POST /gastos/ que supere el acumulado de 500 retorna 400 Bad Request."""
    client, repo = client_y_repo
    # Pre-cargar gasto previo
    repo.guardar(None, usuario_id=1, descripcion="Catering", monto=480.0, categoria="comida")

    payload = {
        "descripcion": "Café",
        "monto": 30.0,
        "categoria": "comida",
    }
    response = client.post("/gastos/", json=payload)
    assert response.status_code == 400
    assert "límite" in response.json()["detail"].lower()


def test_listar_gastos_api(client_y_repo):
    """GET /gastos/ retorna 200 y el listado de gastos del usuario autenticado."""
    client, repo = client_y_repo
    repo.guardar(None, usuario_id=1, descripcion="Gasto 1", monto=10.0, categoria="comida")
    repo.guardar(None, usuario_id=1, descripcion="Gasto 2", monto=20.0, categoria="transporte")
    repo.guardar(None, usuario_id=2, descripcion="Gasto Ajeno", monto=30.0, categoria="otros")

    response = client.get("/gastos/")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2
    assert all(i["usuario_id"] == 1 for i in items)
