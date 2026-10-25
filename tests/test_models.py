"""Pruebas unitarias para los modelos del dominio financiero."""
from datetime import date, timedelta
from decimal import Decimal
import pytest

from src.domain.exceptions import (
    CategoriaInvalidaError, FechaInvalidaError, MontoInvalidoError
)
from src.domain.models import Categoria, TipoTransaccion, Transaccion

class TestCategoria:
    """Casos de prueba para la entidad Categoria."""
    def test_categoria_valida(self)-> None:
        """Verifica que una categoría se crea con nombre normalizado y presupuesto Decimal."""
        cat = Categoria(nombre="alimentación", presupuesto_mensual=350.00)
        assert cat.nombre == "Alimentación"
        assert cat.presupuesto_mensual == Decimal("350.00")
        assert len(cat.id)>10 # Verifica que se generó un UUID automático

    def test_categoria_nombre_vacio_falla(self) ->None:
        """RN-003: El nombre de la categoría no puede estar en blanco."""
        with pytest.raises(CategoriaInvalidaError, match="no puede estar vacío"):
            Categoria(nombre="", presupuesto_mensual=100.00)
        
    def test_categoria_presupuesto_negativo_o_cero_falla(self) ->None:
        """RN-004: El presupuesto debe ser estrictamente mayor a 0."""
        with pytest.raises(MontoInvalidoError):
            Categoria(nombre="Ocio", presupuesto_mensual=0)
        with pytest.raises(MontoInvalidoError):
            Categoria(nombre="Ocio", presupuesto_mensual=-50.00)
        
    def test_actualizar_presupuesto(self) ->None:
        """Verifica que el presupuesto puede actualizarse validando el nuevo monto."""
        cat = Categoria(nombre="Transporte", presupuesto_mensual=120)
        cat.actualizar_presupuesto(180.75)
        assert cat.presupuesto_mensual == Decimal("180.75")

    def test_serializacion_bidireccional(self)-> None:
        """Verifica que to_dict y from_dict conservan la integridad de datos."""
        cat = Categoria(nombre="Salud", presupuesto_mensual=250.00)
        datos = cat.to_dict()
        cat_reconstruida = Categoria.from_dict(datos)
        assert cat_reconstruida.id == cat.id
        assert cat_reconstruida.presupuesto_mensual == cat.presupuesto_mensual

class TestTransaccion:
    """Casos de prueba para la entidad Transaccion."""
    def test_creacion_transaccion_valida(self) -> None:
        """Verifica la creación exitosa de un gasto con fecha por defecto."""
        tx = Transaccion(
            tipo=TipoTransaccion.GASTO,
            monto="45.99",
            categoria_nombre="Supermercado",
            descripcion="Compra semanal",            
        )
        assert tx.tipo == TipoTransaccion.GASTO
        assert tx.monto == Decimal("45.99")
        assert tx.categoria_nombre == "Supermercado"
        assert tx.fecha == date.today()

    def test_monto_cero_o_negativo_falla(self) -> None:    
        """RN-001: Una transacción no puede tener monto <= 0."""
        with pytest.raises(MontoInvalidoError):
            Transaccion(TipoTransaccion.GASTO, 
            monto=0, 
            categoria_nombre="General"
            )
        with pytest.raises(MontoInvalidoError):
            Transaccion(TipoTransaccion.GASTO, 
            monto="-100.50", 
            categoria_nombre="Salario"
            )

    def test_monto_no_numerico_falla(self) -> None:
        """Entradas alfanuméricas inválidas deben lanzar MontoInvalidoError."""
        with pytest.raises(MontoInvalidoError):
            Transaccion(TipoTransaccion.GASTO, 
            monto="gratis", 
            categoria_nombre="Regalo"
            )

    def test_categoria_vacia_falla(self) -> None:
        """RN-003: Toda transacción debe tener una categoría."""
        with pytest.raises(CategoriaInvalidaError):
            Transaccion(TipoTransaccion.GASTO, 
            monto=50,
            categoria_nombre="",            
            )

    def test_fecha_futura_invalida_falla(self) -> None:
        """RN-004: No se permiten fechas con más de 24 horas en el futuro."""
        fecha_futura = date.today() + timedelta(days=5)
        with pytest.raises(FechaInvalidaError, match="no puede ser futura"):
            Transaccion(TipoTransaccion.INGRESO, 
            monto=1000,
            categoria_nombre="Salario",
            fecha=fecha_futura
            )
        
    def test_serializacion_bidireccional(self) -> None:
        """Verifica que to_dict y from_dict conservan tipos y valores exactos."""
        tx_original = Transaccion(
            tipo=TipoTransaccion.INGRESO,
            monto="1500.00",
            categoria_nombre="Salario",
            descripcion="Pago de quincena", 
            fecha=date(2026, 10, 20)           
        )
        data = tx_original.to_dict()
        tx_reconstruida = Transaccion.from_dict(data)
        assert tx_reconstruida.id == tx_original.id
        assert tx_reconstruida.tipo == tx_original.tipo
        assert tx_reconstruida.monto == tx_original.monto
        assert tx_reconstruida.categoria_nombre == tx_original.categoria_nombre
        assert tx_reconstruida.fecha == tx_original.fecha
