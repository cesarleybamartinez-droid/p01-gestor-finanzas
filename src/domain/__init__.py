"""Capa de Dominio: Contiene entidades de negocio y puras excepciones."""

from .exceptions import (
    CategoriaInvalidaError,
    FechaInvalidaError,
    FinanzasError,
    OperacionInvalidaError,
    MontoInvalidoError,
    )

from .models import Categoria, TipoTransaccion, Transaccion

__all__ = [
    "FinanzasError",
    "MontoInvalidoError",
    "CategoriaInvalidaError",
    "FechaInvalidaError",
    "OperacionInvalidaError",
    "Categoria",
    "TipoTransaccion",
    "Transaccion",
    ]
