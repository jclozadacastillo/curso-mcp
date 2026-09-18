"""Servicio de lógica de negocio para gestión de usuarios."""

from app.repositories import usuarios as usuarios_repository
from app.utils.security import hash_password, verify_password


class EmailDuplicadoError(Exception):
    """Excepción lanzada cuando se intenta registrar un email que ya existe."""
    pass


class CredencialesInvalidasError(Exception):
    """Excepción lanzada cuando el login falla por email inexistente o contraseña errónea."""
    pass


def crear_usuario(
    db,
    email: str,
    password: str,
    repo=usuarios_repository,
) -> dict:
    """Registra un nuevo usuario en el sistema validando unicidad de email."""
    if not email or "@" not in email:
        raise ValueError("El correo electrónico no es válido.")
    if not password or len(password) < 6:
        raise ValueError("La contraseña debe contener al menos 6 caracteres.")

    email_normalizado = email.lower().strip()
    existente = repo.obtener_por_email(db, email_normalizado)
    if existente:
        raise EmailDuplicadoError(f"El correo '{email_normalizado}' ya se encuentra registrado.")

    hashed = hash_password(password)
    usuario = repo.guardar(db, email_normalizado, hashed)
    return {"id": usuario.id, "email": usuario.email}


def autenticar_usuario(
    db,
    email: str,
    password: str,
    repo=usuarios_repository,
) -> dict:
    """Valida credenciales de acceso para un usuario."""
    email_normalizado = email.lower().strip() if email else ""
    usuario = repo.obtener_por_email(db, email_normalizado)
    if not usuario or not verify_password(password, usuario.hashed_password):
        raise CredencialesInvalidasError("Credenciales de autenticación incorrectas.")

    return {"id": usuario.id, "email": usuario.email}
