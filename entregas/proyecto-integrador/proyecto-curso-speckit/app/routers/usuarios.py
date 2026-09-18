"""Router de gestión de usuarios y autenticación OAuth2 / JWT."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.usuario import Token, UsuarioCreate, UsuarioOut
from app.services import usuarios as usuarios_service
from app.utils.security import create_access_token

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def registrar_usuario(usuario_in: UsuarioCreate, db: Session = Depends(get_db)):
    """Crea un nuevo usuario delegando al servicio de lógica de negocio."""
    try:
        usuario = usuarios_service.crear_usuario(
            db=db,
            email=usuario_in.email,
            password=usuario_in.password,
        )
        return usuario
    except usuarios_service.EmailDuplicadoError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/token", response_model=Token)
def login_para_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Autentica un usuario y emite un token Bearer JWT con HS256."""
    try:
        usuario = usuarios_service.autenticar_usuario(
            db=db,
            email=form_data.username,
            password=form_data.password,
        )
    except usuarios_service.CredencialesInvalidasError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": usuario["email"]})
    return {"access_token": access_token, "token_type": "bearer"}
