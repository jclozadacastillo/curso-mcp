"""Tests dedicados a los Casos de Error 4 y 5 y flujo de autenticación (Artículo IV y VII.3)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.repositories import gastos as gastos_repo
from app.repositories import usuarios as usuarios_repo


@pytest.fixture
def auth_client():
    """Configura base de datos en memoria para probar el ciclo completo de autenticación y seguridad."""
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

    # Registrar usuario 1
    client.post("/usuarios/", json={"email": "u1@test.com", "password": "password123"})
    # Registrar usuario 2
    client.post("/usuarios/", json={"email": "u2@test.com", "password": "password456"})

    yield client, Session

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_caso_4_sin_token_retorna_401(auth_client):
    """
    Caso de error 4 explícito de spec.md:
    Listar o registrar gastos sin token JWT → 401 Unauthorized.
    """
    client, _ = auth_client

    # Intentar registrar gasto sin header Authorization
    res_post = client.post(
        "/gastos/",
        json={"descripcion": "Sin token", "monto": 20.0, "categoria": "comida"},
    )
    assert res_post.status_code == 401
    assert "detail" in res_post.json()

    # Intentar listar gastos sin header Authorization
    res_get = client.get("/gastos/")
    assert res_get.status_code == 401


def test_caso_4_token_invalido_retorna_401(auth_client):
    """Caso de error 4: Token malformado o adulterado retorna 401."""
    client, _ = auth_client
    headers = {"Authorization": "Bearer token_falso_invalido_xyz"}
    res = client.get("/gastos/", headers=headers)
    assert res.status_code == 401


def test_caso_5_usuario_id_ajeno_ignorado_y_solo_duenio(auth_client):
    """
    Caso de error 5 explícito de spec.md:
    Intentar listar o crear gastos de otro usuario pasando su ID manualmente
    debe ignorarse por completo: el sistema NUNCA acepta ni filtra por un ID enviado
    por el cliente; el usuario_id proviene exclusivamente del JWT decodificado.
    """
    client, Session = auth_client

    # Iniciar sesión como u1
    login_u1 = client.post(
        "/usuarios/token",
        data={"username": "u1@test.com", "password": "password123"},
    )
    assert login_u1.status_code == 200
    token_u1 = login_u1.json()["access_token"]
    headers_u1 = {"Authorization": f"Bearer {token_u1}"}

    # Iniciar sesión como u2
    login_u2 = client.post(
        "/usuarios/token",
        data={"username": "u2@test.com", "password": "password456"},
    )
    token_u2 = login_u2.json()["access_token"]
    headers_u2 = {"Authorization": f"Bearer {token_u2}"}

    # u1 crea un gasto intentando inyectar usuario_id=2 en el payload
    payload_malicioso = {
        "descripcion": "Gasto que pretende ser de U2",
        "monto": 50.0,
        "categoria": "comida",
        "usuario_id": 2,  # Intento de spoofing
    }
    res_crear = client.post("/gastos/", json=payload_malicioso, headers=headers_u1)
    assert res_crear.status_code == 201
    gasto_creado = res_crear.json()

    # Se verifica que se asignó al ID de u1 (el del JWT), ignorando el parámetro
    db = Session()
    u1_db = usuarios_repo.obtener_por_email(db, "u1@test.com")
    u2_db = usuarios_repo.obtener_por_email(db, "u2@test.com")
    db.close()

    assert gasto_creado["usuario_id"] == u1_db.id
    assert gasto_creado["usuario_id"] != u2_db.id

    # u2 consulta sus gastos intentando pasar query param usuario_id=1
    res_listar_u2 = client.get(f"/gastos/?usuario_id={u1_db.id}", headers=headers_u2)
    assert res_listar_u2.status_code == 200
    gastos_u2 = res_listar_u2.json()
    # No ve el gasto de u1
    assert len(gastos_u2) == 0


def test_flujo_registro_usuario_y_login_errores(auth_client):
    """Verifica errores de negocio en registro (email duplicado) y login (credenciales inválidas)."""
    client, _ = auth_client

    # Registro con email duplicado -> 400
    res_dup = client.post("/usuarios/", json={"email": "u1@test.com", "password": "password999"})
    assert res_dup.status_code == 400
    assert "ya se encuentra registrado" in res_dup.json()["detail"]

    # Login con contraseña errónea -> 401
    res_bad_pw = client.post(
        "/usuarios/token",
        data={"username": "u1@test.com", "password": "password_incorrecto"},
    )
    assert res_bad_pw.status_code == 401
