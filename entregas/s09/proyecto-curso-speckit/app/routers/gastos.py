"""Router de operaciones sobre gastos personales."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_gastos_repo
from app.models.usuario import Usuario
from app.schemas.gasto import GastoCreate, GastoOut, GastoUpdateCategoria
from app.services import gastos as gastos_service

router = APIRouter(prefix="/gastos", tags=["gastos"])


@router.post("/", response_model=GastoOut, status_code=status.HTTP_201_CREATED)
def crear_gasto(
    gasto_in: GastoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo=Depends(get_gastos_repo),
):
    """Crea un gasto para el usuario autenticado, delegando al servicio."""
    try:
        nuevo_gasto = gastos_service.registrar_gasto(
            db=db,
            usuario_id=current_user.id,
            descripcion=gasto_in.descripcion,
            monto=gasto_in.monto,
            categoria=gasto_in.categoria,
            repo=repo,
        )
        return nuevo_gasto
    except gastos_service.CategoriaInvalidaError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except gastos_service.LimiteExcedidoError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=list[GastoOut], status_code=status.HTTP_200_OK)
def consultar_gastos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, gt=0),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo=Depends(get_gastos_repo),
):
    """Lista los gastos pertenecientes exclusivamente al usuario autenticado."""
    try:
        return gastos_service.listar_gastos(
            db=db,
            usuario_id=current_user.id,
            skip=skip,
            limit=limit,
            repo=repo,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.patch("/{id}", response_model=GastoOut, status_code=status.HTTP_200_OK)
def modificar_categoria_gasto(
    id: int,
    actualizacion: GastoUpdateCategoria,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo=Depends(get_gastos_repo),
):
    """Permite corregir la categoría de un gasto existente, verificando titularidad."""
    try:
        return gastos_service.actualizar_categoria(
            db=db,
            gasto_id=id,
            usuario_id=current_user.id,
            nueva_categoria=actualizacion.categoria,
            repo=repo,
        )
    except gastos_service.GastoNoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except gastos_service.PermisoDenegadoError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except gastos_service.CategoriaInvalidaError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
