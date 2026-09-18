"""Schemas Pydantic para Gastos."""

from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class CategoriaEnum(str, Enum):
    COMIDA = "comida"
    TRANSPORTE = "transporte"
    ENTRETENIMIENTO = "entretenimiento"
    OTROS = "otros"


class GastoCreate(BaseModel):
    descripcion: str = Field(..., min_length=1)
    monto: float = Field(..., gt=0)
    categoria: str


class GastoOut(BaseModel):
    id: int
    descripcion: str
    monto: float
    categoria: str
    usuario_id: int

    model_config = ConfigDict(from_attributes=True)


class GastoUpdateCategoria(BaseModel):
    categoria: str
