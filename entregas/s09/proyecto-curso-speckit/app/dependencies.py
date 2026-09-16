"""Dependencias de FastAPI para inyección de base de datos, repositorios y autenticación."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.repositories import gastos as gastos_repository
from app.repositories import usuarios as usuarios_repository
from app.utils.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/token")


def get_gastos_repo():
    """Retorna el repositorio de gastos para inyección de dependencias en routers."""
    return gastos_repository


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """Extrae y valida la identidad del usuario desde el token JWT Bearer."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales de autenticación.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    usuario = usuarios_repository.obtener_por_email(db, email=email)
    if usuario is None:
        raise credentials_exception
    return usuario
