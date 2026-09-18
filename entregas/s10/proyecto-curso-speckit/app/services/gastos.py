"""Servicio de lógica de negocio para la gestión de gastos."""

import logging
from app.repositories import gastos as gastos_repository

logger = logging.getLogger(__name__)

LIMITE_POR_CATEGORIA: float = 500.0
CATEGORIAS_VALIDAS: set[str] = {"comida", "transporte", "entretenimiento", "otros"}
# Conformidad con Artículos I.2, II.1, II.3 y VIII.1 de la constitución


class CategoriaInvalidaError(Exception):
    """Excepción lanzada cuando una categoría no forma parte de las permitidas."""
    pass


class LimiteExcedidoError(Exception):
    """Excepción lanzada cuando el gasto proyectado excede el tope de 500 en la categoría."""
    pass


class GastoNoEncontradoError(Exception):
    """Excepción lanzada cuando no se localiza el gasto solicitado."""
    pass


class PermisoDenegadoError(Exception):
    """Excepción lanzada cuando un usuario intenta modificar o acceder a un gasto ajeno."""
    pass


def _validar_descripcion(descripcion: str) -> None:
    """Valida que la descripción no esté vacía ni compuesta exclusivamente por espacios."""
    if not descripcion or not descripcion.strip():
        raise ValueError("La descripción no puede estar vacía.")


def _validar_monto(monto: float) -> None:
    """Valida que el monto sea un valor estrictamente positivo."""
    if monto is None or monto <= 0:
        raise ValueError("El monto debe ser un número estrictamente positivo (> 0).")


def _validar_categoria(categoria: str) -> None:
    """Valida que la categoría corresponda a una de las categorías válidas."""
    if not categoria or categoria.lower() not in CATEGORIAS_VALIDAS:
        raise CategoriaInvalidaError(
            f"Categoría '{categoria}' inválida. Opciones válidas: {sorted(list(CATEGORIAS_VALIDAS))}"
        )


def _validar_limite_acumulado(
    db, usuario_id: int, categoria: str, monto: float, repo=gastos_repository
) -> None:
    """Valida que la suma acumulada de la categoría no exceda el límite mensual de 500.0."""
    total_actual = repo.total_por_categoria(db, usuario_id, categoria.lower())
    if (total_actual + monto) > LIMITE_POR_CATEGORIA:
        raise LimiteExcedidoError(
            f"El gasto de {monto} excede el límite mensual de {LIMITE_POR_CATEGORIA} "
            f"para la categoría '{categoria}'. Total actual acumulado: {total_actual}."
        )


def registrar_gasto(
    db,
    usuario_id: int,
    descripcion: str,
    monto: float,
    categoria: str,
    repo=gastos_repository,
) -> dict:
    """Orquesta la validación y el registro de un nuevo gasto aplicando inversión de dependencias."""
    _validar_descripcion(descripcion)
    _validar_monto(monto)
    categoria_normalizada = categoria.lower().strip() if categoria else ""
    _validar_categoria(categoria_normalizada)
    _validar_limite_acumulado(db, usuario_id, categoria_normalizada, monto, repo=repo)

    return repo.guardar(
        db=db,
        usuario_id=usuario_id,
        descripcion=descripcion.strip(),
        monto=float(monto),
        categoria=categoria_normalizada,
    )


def listar_gastos(
    db,
    usuario_id: int,
    skip: int = 0,
    limit: int = 20,
    repo=gastos_repository,
) -> list[dict]:
    """Retorna los gastos pertenecientes al usuario autenticado, delegando al repositorio."""
    if skip < 0 or limit <= 0:
        raise ValueError("Los parámetros de paginación deben ser positivos (skip >= 0, limit > 0).")
    return repo.listar(db=db, usuario_id=usuario_id, skip=skip, limit=limit)


def actualizar_categoria(
    db,
    gasto_id: int,
    usuario_id: int,
    nueva_categoria: str,
    repo=gastos_repository,
) -> dict:
    """Actualiza la categoría de un gasto existente verificando que el usuario sea el dueño."""
    categoria_normalizada = nueva_categoria.lower().strip() if nueva_categoria else ""
    _validar_categoria(categoria_normalizada)

    gasto = repo.obtener_por_id(db, gasto_id)
    if not gasto:
        raise GastoNoEncontradoError(f"Gasto con id {gasto_id} no encontrado.")

    if gasto["usuario_id"] != usuario_id:
        raise PermisoDenegadoError("No tiene autorización para modificar un gasto que no le pertenece.")

    categoria_anterior = gasto["categoria"]
    gasto_actualizado = repo.actualizar_categoria(db, gasto_id, categoria_normalizada)

    logger.info(
        "Auditoría: Usuario %s actualizó Gasto %s de categoría '%s' a '%s'",
        usuario_id,
        gasto_id,
        categoria_anterior,
        categoria_normalizada,
    )
    return gasto_actualizado
