"""Tests unitarios de services/gastos.py con RepositorioFalso (DIP, sin unittest.mock)."""

import pytest
from app.services.gastos import (
    LIMITE_POR_CATEGORIA,
    CategoriaInvalidaError,
    GastoNoEncontradoError,
    LimiteExcedidoError,
    PermisoDenegadoError,
    actualizar_categoria,
    listar_gastos,
    registrar_gasto,
)


class RepositorioFalso:
    """
    Repositorio simulado en memoria que cumple el mismo contrato que app.repositories.gastos.
    Permite testear services/ aplicando DIP sin usar unittest.mock (Artículo VII.2).
    """

    def __init__(self):
        self.gastos: list[dict] = []
        self._contador_id = 1

    def guardar(self, db, usuario_id: int, descripcion: str, monto: float, categoria: str) -> dict:
        gasto = {
            "id": self._contador_id,
            "usuario_id": usuario_id,
            "descripcion": descripcion,
            "monto": float(monto),
            "categoria": categoria,
        }
        self.gastos.append(gasto)
        self._contador_id += 1
        return gasto

    def listar(self, db, usuario_id: int, skip: int = 0, limit: int = 20) -> list[dict]:
        filtrados = [g for g in self.gastos if g["usuario_id"] == usuario_id]
        return filtrados[skip : skip + limit]

    def total_por_categoria(self, db, usuario_id: int, categoria: str) -> float:
        return sum(
            g["monto"]
            for g in self.gastos
            if g["usuario_id"] == usuario_id and g["categoria"] == categoria
        )

    def obtener_por_id(self, db, gasto_id: int) -> dict | None:
        for g in self.gastos:
            if g["id"] == gasto_id:
                return g
        return None

    def actualizar_categoria(self, db, gasto_id: int, nueva_categoria: str) -> dict | None:
        for g in self.gastos:
            if g["id"] == gasto_id:
                g["categoria"] = nueva_categoria
                return g
        return None


@pytest.fixture
def repo_falso():
    return RepositorioFalso()


def test_registrar_gasto_exito(repo_falso):
    """Verifica el registro exitoso de un gasto dentro del límite permitido."""
    gasto = registrar_gasto(
        db=None,
        usuario_id=1,
        descripcion="Almuerzo ejecutivo",
        monto=25.50,
        categoria="comida",
        repo=repo_falso,
    )
    assert gasto["id"] == 1
    assert gasto["usuario_id"] == 1
    assert gasto["descripcion"] == "Almuerzo ejecutivo"
    assert gasto["monto"] == 25.50
    assert gasto["categoria"] == "comida"
    assert len(repo_falso.gastos) == 1


def test_registrar_gasto_monto_cero_o_negativo(repo_falso):
    """Caso 1 de error: Rechazar montos <= 0."""
    with pytest.raises(ValueError, match="El monto debe ser un número estrictamente positivo"):
        registrar_gasto(
            db=None,
            usuario_id=1,
            descripcion="Gasto inválido",
            monto=0.0,
            categoria="comida",
            repo=repo_falso,
        )

    with pytest.raises(ValueError, match="El monto debe ser un número estrictamente positivo"):
        registrar_gasto(
            db=None,
            usuario_id=1,
            descripcion="Gasto negativo",
            monto=-15.0,
            categoria="comida",
            repo=repo_falso,
        )


def test_registrar_gasto_descripcion_vacia(repo_falso):
    """Verifica que descripciones vacías o con puros espacios sean rechazadas."""
    with pytest.raises(ValueError, match="La descripción no puede estar vacía"):
        registrar_gasto(
            db=None,
            usuario_id=1,
            descripcion="   ",
            monto=10.0,
            categoria="comida",
            repo=repo_falso,
        )


def test_registrar_gasto_categoria_invalida(repo_falso):
    """Caso 2 de error: Categoría inexistente lanza CategoriaInvalidaError."""
    with pytest.raises(CategoriaInvalidaError):
        registrar_gasto(
            db=None,
            usuario_id=1,
            descripcion="Boleto espacial",
            monto=100.0,
            categoria="aeronautica",
            repo=repo_falso,
        )


def test_registrar_gasto_limite_excedido(repo_falso):
    """Caso 3 de error: Total acumulado mensual que supere 500 lanza LimiteExcedidoError."""
    # Primer gasto de 400 en comida (válido)
    registrar_gasto(
        db=None,
        usuario_id=1,
        descripcion="Supermercado mensual",
        monto=400.0,
        categoria="comida",
        repo=repo_falso,
    )
    assert repo_falso.total_por_categoria(None, 1, "comida") == 400.0

    # Segundo gasto de 150 en comida (400 + 150 = 550 > 500 -> Excede límite)
    with pytest.raises(LimiteExcedidoError):
        registrar_gasto(
            db=None,
            usuario_id=1,
            descripcion="Cena de celebración",
            monto=150.0,
            categoria="comida",
            repo=repo_falso,
        )


def test_listar_gastos(repo_falso):
    """Verifica que listar gastos aplique paginación y devuelva solo los del usuario."""
    registrar_gasto(None, 1, "Gasto U1-A", 10.0, "comida", repo=repo_falso)
    registrar_gasto(None, 1, "Gasto U1-B", 20.0, "transporte", repo=repo_falso)
    registrar_gasto(None, 2, "Gasto U2", 30.0, "otros", repo=repo_falso)

    gastos_u1 = listar_gastos(None, 1, skip=0, limit=10, repo=repo_falso)
    assert len(gastos_u1) == 2
    assert all(g["usuario_id"] == 1 for g in gastos_u1)

    gastos_paginados = listar_gastos(None, 1, skip=1, limit=1, repo=repo_falso)
    assert len(gastos_paginados) == 1
    assert gastos_paginados[0]["descripcion"] == "Gasto U1-B"


def test_actualizar_categoria_exito_y_errores(repo_falso):
    """Verifica actualización de categoría y control de dueño (Reto Paso 4)."""
    gasto = registrar_gasto(None, 1, "Taxi al aeropuerto", 30.0, "otros", repo=repo_falso)

    # Actualización exitosa por el dueño
    actualizado = actualizar_categoria(
        None,
        gasto_id=gasto["id"],
        usuario_id=1,
        nueva_categoria="transporte",
        repo=repo_falso,
    )
    assert actualizado["categoria"] == "transporte"

    # Intento de actualización por un usuario distinto (403 / PermisoDenegadoError)
    with pytest.raises(PermisoDenegadoError):
        actualizar_categoria(
            None,
            gasto_id=gasto["id"],
            usuario_id=99,
            nueva_categoria="comida",
            repo=repo_falso,
        )

    # Gasto inexistente (404 / GastoNoEncontradoError)
    with pytest.raises(GastoNoEncontradoError):
        actualizar_categoria(
            None,
            gasto_id=9999,
            usuario_id=1,
            nueva_categoria="comida",
            repo=repo_falso,
        )
