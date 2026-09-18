"""Esquemas Pydantic para el dominio de Reservas."""

from datetime import date, time, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReservaBase(BaseModel):
    espacio: str = Field(..., min_length=2, max_length=100, description="Identificador o nombre del espacio")
    fecha: date = Field(..., description="Fecha de la reserva (YYYY-MM-DD)")
    hora_inicio: time = Field(..., description="Hora de inicio (HH:MM)")
    hora_fin: time = Field(..., description="Hora de finalización (HH:MM)")
    motivo: Optional[str] = Field(default="", max_length=255, description="Propósito o motivo de la reserva")

    @field_validator("espacio")
    @classmethod
    def normalizar_espacio(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if not v_clean:
            raise ValueError("El espacio no puede estar vacío")
        return v_clean


class ReservaCreate(ReservaBase):
    pass


class ReservaResponse(ReservaBase):
    id: int
    usuario_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IntervaloOcupado(BaseModel):
    hora_inicio: time
    hora_fin: time
    motivo: Optional[str] = ""

    model_config = ConfigDict(from_attributes=True)


class DisponibilidadResponse(BaseModel):
    espacio: str
    fecha: date
    reservas_ocupadas: List[IntervaloOcupado]
    total_ocupado: int
