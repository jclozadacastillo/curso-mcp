"""Punto de entrada principal de la aplicación FastAPI."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.database import Base, engine
from app.routers.gastos import router as gastos_router
from app.routers.usuarios import router as usuarios_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida de la aplicación: asegura la inicialización de tablas."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Sistema de Control de Gastos",
    description="API REST y MCP para la gestión y control de gastos personales con Spec-Driven Development",
    version="1.0.0",
    lifespan=lifespan,
)

# Inclusión de routers modulares
app.include_router(usuarios_router)
app.include_router(gastos_router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Manejador global para excepciones no controladas (Artículo IV.5 de la constitución)."""
    logger.exception("Error no controlado procesando la solicitud %s: %s", request.url, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error interno del servidor"},
    )
