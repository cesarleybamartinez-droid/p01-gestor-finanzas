"""Pruebas unitarias para la capa de servicios (ServicioFinanzas)."""

from datetime import date
from decimal import Decimal
from pathlib import Path
import pytest

from src.domain.exceptions import CategoriaInvalidaError
from src.domain.models import TipoTransaccion
from src.persistence.repository import RepositorioFinanzas
from src.services.finance_service import ServicioFinanzas


@pytest.fixture
def servicio(tmp_path: Path) -> ServicioFinanzas:
    """Fixture que crea un servicio respaldado por un repositorio temporal."""
    repo = RepositorioFinanzas(ruta_archivo=tmp_path / "test_service.json")
    return ServicioFinanzas(repositorio=repo)


class TestServicioFinanzas:
    """Pruebas de las reglas de negocio en la capa de servicios."""

    def test_registrar_transaccion_con_categoria_inexistente_falla(
        self, servicio: ServicioFinanzas
    ) -> None:
        """RN-003: No se puede registrar un gasto en una categoría no registrada."""
        with pytest.raises(CategoriaInvalidaError, match="no existe"):
            servicio.registrar_transaccion(
                tipo=TipoTransaccion.GASTO,
                monto="50.00",
                categoria_nombre="Viajes",  # No ha sido creada
            )

    def test_alerta_presupuesto_excedido(self, servicio: ServicioFinanzas) -> None:
        """RF-004 & RN-005: Al superar el presupuesto mensual se emite una alerta explícita."""
        servicio.registrar_categoria("Restaurantes", presupuesto_mensual="100.00")

        # Gasto 1: $70 (70% consumido, estado normal)
        _, alerta1 = servicio.registrar_transaccion(
            tipo=TipoTransaccion.GASTO,
            monto="70.00",
            categoria_nombre="Restaurantes",
            fecha=date(2026, 10, 1),
        )
        assert alerta1 is None

        # Gasto 2: $40 más (Total $110, supera los $100 -> debe emitir alerta)
        _, alerta2 = servicio.registrar_transaccion(
            tipo=TipoTransaccion.GASTO,
            monto="40.00",
            categoria_nombre="Restaurantes",
            fecha=date(2026, 10, 5),
        )
        assert alerta2 is not None
        assert "excedido el presupuesto" in alerta2
        assert "$10.00" in alerta2  # Exceso exacto

    def test_balance_mensual_calculo_correcto(
        self, servicio: ServicioFinanzas
    ) -> None:
        """RF-005: El balance mensual suma ingresos, gastos y calcula el saldo neto."""
        servicio.registrar_categoria("Sueldo", presupuesto_mensual="1000.00")
        servicio.registrar_categoria("Comida", presupuesto_mensual="300.00")

        # Ingreso de $2000 en octubre
        servicio.registrar_transaccion(
            tipo=TipoTransaccion.INGRESO,
            monto="2000.00",
            categoria_nombre="Sueldo",
            fecha=date(2026, 10, 1),
        )
        # Gasto de $150 en octubre
        servicio.registrar_transaccion(
            tipo=TipoTransaccion.GASTO,
            monto="150.00",
            categoria_nombre="Comida",
            fecha=date(2026, 10, 10),
        )

        balance = servicio.obtener_balance_mensual(anio=2026, mes=10)
        assert balance.total_ingresos == Decimal("2000.00")
        assert balance.total_gastos == Decimal("150.00")
        assert balance.saldo_neto == Decimal("1850.00")

    def test_filtrar_transacciones_por_mes_y_categoria(
        self, servicio: ServicioFinanzas
    ) -> None:
        """RF-007: Se pueden filtrar transacciones por año, mes y categoría."""
        servicio.registrar_categoria("Comida", presupuesto_mensual="300.00")

        servicio.registrar_transaccion(
            tipo=TipoTransaccion.GASTO,
            monto="20.00",
            categoria_nombre="Comida",
            fecha=date(2026, 9, 15),  # Septiembre
        )
        servicio.registrar_transaccion(
            tipo=TipoTransaccion.GASTO,
            monto="30.00",
            categoria_nombre="Comida",
            fecha=date(2026, 10, 15),  # Octubre
        )

        # Filtrar solo octubre
        octubre = servicio.listar_transacciones(anio=2026, mes=10)
        assert len(octubre) == 1
        assert octubre[0].monto == Decimal("30.00")
