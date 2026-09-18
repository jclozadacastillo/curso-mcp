"""Tests unitarios complementarios para asegurar cobertura superior al 90% en services/ y 80% global."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.models.usuario import Usuario
from app.repositories import usuarios as usuarios_repo
from app.services import usuarios as usuarios_service
from app.services import gastos as gastos_service
from app.utils.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from datetime import timedelta


@pytest.fixture
def memory_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_security_utils():
    """Verifica funciones puras de criptografía y JWT."""
    pw = "mi_password_segura_123"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed) is True
    assert verify_password("otra_password", hashed) is False

    # Token con expiración personalizada
    token = create_access_token({"sub": "admin@test.com"}, expires_delta=timedelta(minutes=5))
    payload = decode_access_token(token)
    assert payload["sub"] == "admin@test.com"

    # Token expirado o alterado
    with pytest.raises(ValueError, match="Token inválido o expirado"):
        decode_access_token("token.totalmente.invalido")


def test_get_db_generator():
    """Verifica que el generador get_db ceda una sesión y la cierre adecuadamente."""
    gen = get_db()
    session = next(gen)
    assert session is not None
    try:
        next(gen)
    except StopIteration:
        pass


def test_services_usuarios_validaciones(memory_db):
    """Verifica validaciones de entrada en creación y autenticación de usuarios."""
    # Email inválido
    with pytest.raises(ValueError, match="correo electrónico no es válido"):
        usuarios_service.crear_usuario(memory_db, email="invalido_sin_arroba", password="password123")

    # Contraseña muy corta
    with pytest.raises(ValueError, match="al menos 6 caracteres"):
        usuarios_service.crear_usuario(memory_db, email="valido@test.com", password="123")

    # Crear exitoso
    u = usuarios_service.crear_usuario(memory_db, email="valido@test.com", password="password123")
    assert u["email"] == "valido@test.com"

    # Intentar duplicar
    with pytest.raises(usuarios_service.EmailDuplicadoError):
        usuarios_service.crear_usuario(memory_db, email="valido@test.com", password="password123")

    # Autenticación exitosa
    auth = usuarios_service.autenticar_usuario(memory_db, email="valido@test.com", password="password123")
    assert auth["email"] == "valido@test.com"

    # Autenticación con password errónea
    with pytest.raises(usuarios_service.CredencialesInvalidasError):
        usuarios_service.autenticar_usuario(memory_db, email="valido@test.com", password="erronea_password")

    # Autenticación con email inexistente
    with pytest.raises(usuarios_service.CredencialesInvalidasError):
        usuarios_service.autenticar_usuario(memory_db, email="no_existe@test.com", password="cualquier_password")


def test_services_gastos_paginacion_invalida():
    """Verifica que parámetros negativos en listar_gastos disparen ValueError."""
    from tests.test_gastos import RepositorioFalso

    repo = RepositorioFalso()
    with pytest.raises(ValueError, match="Los parámetros de paginación deben ser positivos"):
        gastos_service.listar_gastos(None, usuario_id=1, skip=-1, limit=10, repo=repo)

    with pytest.raises(ValueError, match="Los parámetros de paginación deben ser positivos"):
        gastos_service.listar_gastos(None, usuario_id=1, skip=0, limit=0, repo=repo)


def test_dependencies_edge_cases(memory_db):
    """Verifica casos extremos en dependencias de autenticación."""
    from fastapi import HTTPException
    from app.dependencies import get_current_user

    # Token sin sub
    token_sin_sub = create_access_token({})
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token_sin_sub, db=memory_db)
    assert exc_info.value.status_code == 401

    # Token con email que no existe en BD
    token_inexistente = create_access_token({"sub": "fantasma@test.com"})
    with pytest.raises(HTTPException) as exc_info2:
        get_current_user(token=token_inexistente, db=memory_db)
    assert exc_info2.value.status_code == 401


def test_routers_value_error_handling():
    """Verifica que los routers traduzcan ValueError a HTTP 400."""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.dependencies import get_current_user, get_db
    from app.models.usuario import Usuario

    client = TestClient(app)
    app.dependency_overrides[get_current_user] = lambda: Usuario(id=1, email="test@test.com", hashed_password="h")
    app.dependency_overrides[get_db] = lambda: None

    # POST /gastos/ con descripcion vacía dispara ValueError en service -> router responde 400
    res = client.post("/gastos/", json={"descripcion": "   ", "monto": 10.0, "categoria": "comida"})
    assert res.status_code == 400
    assert "no puede estar vacía" in res.json()["detail"]

    # POST /usuarios/ con password corta dispara ValueError en service -> router responde 400
    res_u = client.post("/usuarios/", json={"email": "usuario@nuevo.com", "password": "123"})
    assert res_u.status_code == 400

    app.dependency_overrides.clear()


def test_repositories_obtener_por_id_inexistente(memory_db):
    """Verifica que obtener_por_id devuelva None si el gasto no existe."""
    from app.repositories import gastos as gastos_repo
    assert gastos_repo.obtener_por_id(memory_db, 99999) is None
    assert gastos_repo.actualizar_categoria(memory_db, 99999, "comida") is None

