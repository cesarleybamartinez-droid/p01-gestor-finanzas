"""Pruebas unitarias para la capa de persistencia (RepositorioFinanzas)."""

from decimal import Decimal
from pathlib import Path
import pytest

from src.domain.models import Categoria, TipoTransaccion, Transaccion
from src.persistence.repository import RepositorioFinanzas

@pytest.fixture
def repo(tmp_path:Path) -> RepositorioFinanzas:
    """Fixture que provee un repositorio apuntando a un archivo temporal aislado."""
    ruta_test = tmp_path / "test_finanzas.json"
    return RepositorioFinanzas(ruta_archivo=ruta_test)

class TestRepositorioFinanzas:
    """Casos de prueba para verificar la persistencia atómica."""
    def test_inicializacion_crea_archivo_vacio(self, repo: RepositorioFinanzas)->None:
        """Verifica que el archivo JSON se inicializa con la estructura base."""
        assert repo.ruta_archivo.exists()
        assert repo.obtener_todas_las_categorias() == []
        assert repo.obtener_todas_las_transacciones() == []

    def test_guardar_y_obtener_categoria(self, repo: RepositorioFinanzas) ->None:
        """Verifica la persistencia y recuperación de una categoría."""
        # 1. Crear una instancia de Categoria
        cat = Categoria(nombre="Alimentacion", presupuesto_mensual=Decimal("400.00"))

        # 2. Guardarla
        repo.guardar_categoria(cat)

        #3. Obtenerla
        recuperada = repo.obtener_categoria("Alimentacion")  # Busca sin importar mayúsculas

        #4. Assertions
        assert recuperada is not None
        assert recuperada.nombre == "Alimentacion"
        assert recuperada.presupuesto_mensual == Decimal("400.00")

    def test_guardar_y_obtener_transaccion(self, repo: RepositorioFinanzas) ->None:
        """Verifica que una transacción se guarda y se recupera con su tipo y monto intactos."""
        # 1. Crear una instancia de Transaccion
        tx = Transaccion(
            monto="50.00", 
            tipo=TipoTransaccion.GASTO, 
            descripcion="Almuerzo de trabajo",
            categoria_nombre ="Alimentacion"
        )
        # 2. Guardarla
        repo.guardar_transaccion(tx)
        todas = repo.obtener_todas_las_transacciones()
        assert len(todas) == 1
        assert todas[0].monto == Decimal("50.00")
        assert todas[0].tipo == TipoTransaccion.GASTO
        assert todas[0].descripcion == "Almuerzo de trabajo"