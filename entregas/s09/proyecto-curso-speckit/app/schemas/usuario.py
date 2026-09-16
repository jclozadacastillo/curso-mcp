"""Schemas Pydantic para Usuarios y Tokens."""

from pydantic import BaseModel, ConfigDict, EmailStr


class UsuarioCreate(BaseModel):
    email: EmailStr
    password: str


class UsuarioOut(BaseModel):
    id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: str | None = None
