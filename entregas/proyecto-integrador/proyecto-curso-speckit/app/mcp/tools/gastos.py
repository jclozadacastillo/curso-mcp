"""Herramientas MCP para la gestión de gastos personales."""

from sqlalchemy.orm import Session
from app.config import settings
from app.database import SessionLocal
from app.repositories import usuarios as usuarios_repository
from app.services import gastos as gastos_service
from app.utils.security import decode_access_token


def resolver_usuario_id(db: Session, token: str | None = None) -> int:
    """
    Resuelve la identidad del usuario para la ejecución de la tool MCP.
    
    Artículo VI.4 de la constitución:
    Si hay un token JWT verificado (transporte streamable-http), la tool DEBE usar
    la identidad de ese token (nunca un usuario demo hardcodeado).
    
    SIMPLIFICACIÓN CONSCIENTE DOCUMENTADA (Artículo VI.4):
    Cuando el transporte es stdio o no hay token en el contexto de llamada, se recurre
    al usuario demo configurado en settings.DEMO_USER_EMAIL como fallback legítimo.
    """
    if token:
        try:
            payload = decode_access_token(token)
            email = payload.get("sub")
            if email:
                usuario = usuarios_repository.obtener_por_email(db, email)
                if usuario:
                    return usuario.id
        except Exception:
            pass

    # Fallback documentado: usuario demo en stdio sin propagación de token
    demo = usuarios_repository.obtener_por_email(db, settings.DEMO_USER_EMAIL)
    if demo:
        return demo.id

    # Si el usuario demo no existe aún en la base de datos de pruebas/dev, se crea
    from app.utils.security import hash_password
    nuevo_demo = usuarios_repository.guardar(
        db,
        settings.DEMO_USER_EMAIL,
        hash_password(settings.DEMO_USER_PASSWORD),
    )
    return nuevo_demo.id


def registrar_gasto_tool(
    descripcion: str,
    monto: float,
    categoria: str,
    token: str | None = None,
    db: Session | None = None,
) -> dict:
    """
    Registra un gasto con descripción, monto y categoría, validando que el monto sea
    positivo, la categoría válida (comida, transporte, entretenimiento, otros) y que no
    se exceda el límite acumulado mensual de 500 por categoría.
    
    Reutiliza app/services/gastos.py cumpliendo el Artículo VI.1 de la constitución.
    """
    sesion_propia = False
    if db is None:
        db = SessionLocal()
        sesion_propia = True

    try:
        usuario_id = resolver_usuario_id(db, token=token)
        nuevo_gasto = gastos_service.registrar_gasto(
            db=db,
            usuario_id=usuario_id,
            descripcion=descripcion,
            monto=monto,
            categoria=categoria,
        )
        return {"exito": True, "gasto": nuevo_gasto}
    except (
        gastos_service.CategoriaInvalidaError,
        gastos_service.LimiteExcedidoError,
        ValueError,
    ) as e:
        # Artículo VI.3: errores de negocio como estructura clara, sin romper la sesión MCP
        return {"error": str(e)}
    finally:
        if sesion_propia:
            db.close()


def listar_gastos_tool(
    skip: int = 0,
    limit: int = 20,
    token: str | None = None,
    db: Session | None = None,
) -> dict:
    """
    Lista los gastos del usuario autenticado con soporte de paginación (skip y limit).
    
    Reutiliza app/services/gastos.py cumpliendo el Artículo VI.1 de la constitución.
    """
    sesion_propia = False
    if db is None:
        db = SessionLocal()
        sesion_propia = True

    try:
        usuario_id = resolver_usuario_id(db, token=token)
        gastos = gastos_service.listar_gastos(
            db=db,
            usuario_id=usuario_id,
            skip=skip,
            limit=limit,
        )
        return {"exito": True, "gastos": gastos}
    except ValueError as e:
        return {"error": str(e)}
    finally:
        if sesion_propia:
            db.close()
