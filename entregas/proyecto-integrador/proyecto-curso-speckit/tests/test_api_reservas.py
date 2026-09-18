"""Pruebas de la API REST de Reservas de Espacios con TestClient y autenticación real.

Valida todos los endpoints REST, códigos de estado HTTP (201, 200, 204, 400, 401, 403, 404, 422),
aislamiento horizontal entre usuarios y confirmación obligatoria de servidor.
"""

from datetime import date, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def api_client():
    """Configura SQLite en memoria para tests de integración REST."""
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

    # Registro de Usuario 1
    client.post("/usuarios/", json={"email": "u1@reservas.com", "password": "password123"})
    resp_token_u1 = client.post(
        "/usuarios/token",
        data={"username": "u1@reservas.com", "password": "password123"},
    )
    token_u1 = resp_token_u1.json()["access_token"]
    headers_u1 = {"Authorization": f"Bearer {token_u1}"}

    # Registro de Usuario 2
    client.post("/usuarios/", json={"email": "u2@reservas.com", "password": "password456"})
    resp_token_u2 = client.post(
        "/usuarios/token",
        data={"username": "u2@reservas.com", "password": "password456"},
    )
    token_u2 = resp_token_u2.json()["access_token"]
    headers_u2 = {"Authorization": f"Bearer {token_u2}"}

    yield client, headers_u1, headers_u2

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_crear_reserva_api_exito(api_client):
    """POST /reservas/ con datos válidos y token retorna 201 Created."""
    client, headers_u1, _ = api_client
    fecha_futura = (date.today() + timedelta(days=2)).isoformat()
    payload = {
        "espacio": "sala-a",
        "fecha": fecha_futura,
        "hora_inicio": "10:00:00",
        "hora_fin": "11:30:00",
        "motivo": "Reunión de arquitectura",
    }
    response = client.post("/reservas/", json=payload, headers=headers_u1)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["espacio"] == "sala-a"
    assert data["fecha"] == fecha_futura
    assert "10:00" in data["hora_inicio"]
    assert "11:30" in data["hora_fin"]


def test_crear_reserva_api_sin_token_401(api_client):
    """Acceso a /reservas/ sin cabecera Authorization retorna 401 Unauthorized."""
    client, _, _ = api_client
    fecha_futura = (date.today() + timedelta(days=2)).isoformat()
    payload = {
        "espacio": "sala-a",
        "fecha": fecha_futura,
        "hora_inicio": "10:00:00",
        "hora_fin": "11:00:00",
    }
    response = client.post("/reservas/", json=payload)
    assert response.status_code == 401


def test_crear_reserva_api_token_invalido_401(api_client):
    """Acceso a /reservas/ con token JWT alterado o inválido retorna 401 Unauthorized."""
    client, _, _ = api_client
    fecha_futura = (date.today() + timedelta(days=2)).isoformat()
    payload = {
        "espacio": "sala-a",
        "fecha": fecha_futura,
        "hora_inicio": "10:00:00",
        "hora_fin": "11:00:00",
    }
    response = client.post(
        "/reservas/",
        json=payload,
        headers={"Authorization": "Bearer token.invalido.firmainvalida"},
    )
    assert response.status_code == 401


def test_crear_reserva_solapamiento_400(api_client):
    """RN-01: Intentar reservar un horario ya ocupado retorna 400 Bad Request."""
    client, headers_u1, headers_u2 = api_client
    fecha_futura = (date.today() + timedelta(days=3)).isoformat()

    # Usuario 1 reserva de 14:00 a 16:00
    res1 = client.post(
        "/reservas/",
        json={
            "espacio": "cancha-tenis",
            "fecha": fecha_futura,
            "hora_inicio": "14:00:00",
            "hora_fin": "16:00:00",
            "motivo": "Partido u1",
        },
        headers=headers_u1,
    )
    assert res1.status_code == 201

    # Usuario 2 intenta reservar de 15:00 a 17:00 en la misma cancha y fecha
    res2 = client.post(
        "/reservas/",
        json={
            "espacio": "cancha-tenis",
            "fecha": fecha_futura,
            "hora_inicio": "15:00:00",
            "hora_fin": "17:00:00",
            "motivo": "Partido u2",
        },
        headers=headers_u2,
    )
    assert res2.status_code == 400
    assert "Conflicto de horario" in res2.json()["detail"]


def test_crear_reserva_borde_exacto_201(api_client):
    """RN-01b: Reservas consecutivas que se tocan en el borde exacto son permitidas."""
    client, headers_u1, headers_u2 = api_client
    fecha_futura = (date.today() + timedelta(days=3)).isoformat()

    # U1: 09:00 a 10:00
    r1 = client.post(
        "/reservas/",
        json={
            "espacio": "consultorio-1",
            "fecha": fecha_futura,
            "hora_inicio": "09:00:00",
            "hora_fin": "10:00:00",
        },
        headers=headers_u1,
    )
    assert r1.status_code == 201

    # U2: 10:00 a 11:00 (mismo espacio, borde exacto)
    r2 = client.post(
        "/reservas/",
        json={
            "espacio": "consultorio-1",
            "fecha": fecha_futura,
            "hora_inicio": "10:00:00",
            "hora_fin": "11:00:00",
        },
        headers=headers_u2,
    )
    assert r2.status_code == 201


def test_crear_reserva_horarios_invalidos_400(api_client):
    """RN-02: hora_fin <= hora_inicio retorna 400 Bad Request."""
    client, headers_u1, _ = api_client
    fecha_futura = (date.today() + timedelta(days=1)).isoformat()

    res = client.post(
        "/reservas/",
        json={
            "espacio": "sala-a",
            "fecha": fecha_futura,
            "hora_inicio": "11:00:00",
            "hora_fin": "10:00:00",
        },
        headers=headers_u1,
    )
    assert res.status_code == 400
    assert "posterior" in res.json()["detail"]


def test_crear_reserva_fecha_pasada_400(api_client):
    """RN-02b: Fecha en el pasado retorna 400 Bad Request."""
    client, headers_u1, _ = api_client
    fecha_pasada = (date.today() - timedelta(days=2)).isoformat()

    res = client.post(
        "/reservas/",
        json={
            "espacio": "sala-a",
            "fecha": fecha_pasada,
            "hora_inicio": "10:00:00",
            "hora_fin": "11:00:00",
        },
        headers=headers_u1,
    )
    assert res.status_code == 400
    assert "anterior a la fecha actual" in res.json()["detail"]


def test_crear_reserva_formato_invalido_422(api_client):
    """Envío de datos malformados retorna 422 Unprocessable Entity."""
    client, headers_u1, _ = api_client
    res = client.post(
        "/reservas/",
        json={"espacio": "x", "fecha": "fecha-no-valida"},
        headers=headers_u1,
    )
    assert res.status_code == 422


def test_listar_reservas_aislamiento_y_paginacion(api_client):
    """GET /reservas/ retorna únicamente las reservas del usuario autenticado."""
    client, headers_u1, headers_u2 = api_client
    fecha = (date.today() + timedelta(days=4)).isoformat()

    # U1 crea 2 reservas
    client.post(
        "/reservas/",
        json={"espacio": "sala-1", "fecha": fecha, "hora_inicio": "08:00:00", "hora_fin": "09:00:00"},
        headers=headers_u1,
    )
    client.post(
        "/reservas/",
        json={"espacio": "sala-2", "fecha": fecha, "hora_inicio": "09:00:00", "hora_fin": "10:00:00"},
        headers=headers_u1,
    )

    # U2 crea 1 reserva
    client.post(
        "/reservas/",
        json={"espacio": "sala-3", "fecha": fecha, "hora_inicio": "10:00:00", "hora_fin": "11:00:00"},
        headers=headers_u2,
    )

    # Listar U1
    res_u1 = client.get("/reservas/", headers=headers_u1)
    assert res_u1.status_code == 200
    assert len(res_u1.json()) == 2

    # Listar U2
    res_u2 = client.get("/reservas/", headers=headers_u2)
    assert res_u2.status_code == 200
    assert len(res_u2.json()) == 1


def test_consultar_disponibilidad_api(api_client):
    """GET /reservas/disponibilidad retorna los rangos ocupados."""
    client, headers_u1, _ = api_client
    fecha = (date.today() + timedelta(days=5)).isoformat()
    client.post(
        "/reservas/",
        json={"espacio": "sala-reuniones", "fecha": fecha, "hora_inicio": "10:00:00", "hora_fin": "11:00:00"},
        headers=headers_u1,
    )

    res = client.get(
        f"/reservas/disponibilidad?espacio=sala-reuniones&fecha={fecha}",
        headers=headers_u1,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["espacio"] == "sala-reuniones"
    assert data["total_ocupado"] == 1
    assert len(data["reservas_ocupadas"]) == 1


def test_obtener_reserva_propia_y_ajena_403(api_client):
    """GET /reservas/{id} permite acceso propio, y retorna 403 ante acceso ajeno."""
    client, headers_u1, headers_u2 = api_client
    fecha = (date.today() + timedelta(days=5)).isoformat()
    post_res = client.post(
        "/reservas/",
        json={"espacio": "sala-vip", "fecha": fecha, "hora_inicio": "12:00:00", "hora_fin": "13:00:00"},
        headers=headers_u1,
    )
    reserva_id = post_res.json()["id"]

    # Acceso por dueño (U1) -> 200
    r_propia = client.get(f"/reservas/{reserva_id}", headers=headers_u1)
    assert r_propia.status_code == 200

    # Acceso por otro usuario (U2) -> 403 Forbidden
    r_ajena = client.get(f"/reservas/{reserva_id}", headers=headers_u2)
    assert r_ajena.status_code == 403

    # Acceso a ID inexistente -> 404 Not Found
    r_inexistente = client.get("/reservas/9999", headers=headers_u1)
    assert r_inexistente.status_code == 404


def test_cancelar_reserva_ciclo_completo(api_client):
    """DELETE /reservas/{id} valida confirmación, propiedad y persistencia."""
    client, headers_u1, headers_u2 = api_client
    fecha = (date.today() + timedelta(days=6)).isoformat()
    res = client.post(
        "/reservas/",
        json={"espacio": "cancha-futbol", "fecha": fecha, "hora_inicio": "16:00:00", "hora_fin": "18:00:00"},
        headers=headers_u1,
    )
    reserva_id = res.json()["id"]

    # 1. Cancelar sin confirmacion -> 400 Bad Request
    sin_conf = client.delete(f"/reservas/{reserva_id}", headers=headers_u1)
    assert sin_conf.status_code == 400
    assert "confirmar explícitamente" in sin_conf.json()["detail"]

    # 2. Cancelar con confirmacion por usuario ajeno (U2) -> 403 Forbidden
    ajena = client.delete(f"/reservas/{reserva_id}?confirmacion=true", headers=headers_u2)
    assert ajena.status_code == 403

    # 3. Cancelar reserva inexistente -> 404 Not Found
    inex = client.delete("/reservas/9999?confirmacion=true", headers=headers_u1)
    assert inex.status_code == 404

    # 4. Cancelar con éxito por el dueño con confirmacion=true -> 204 No Content
    exito = client.delete(f"/reservas/{reserva_id}?confirmacion=true", headers=headers_u1)
    assert exito.status_code == 204

    # 5. Verificar que ya no existe -> 404
    verif = client.get(f"/reservas/{reserva_id}", headers=headers_u1)
    assert verif.status_code == 404
