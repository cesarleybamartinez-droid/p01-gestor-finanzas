"""Servicio principal de finanzas personales.

Orquesta los casos de uso:
- RF-001: Definición y actualización de categorías.
- RF-002: Registro de transacciones con validación de existencia de categoría.
- RF-004: Alerta si el gasto acumulado supera el presupuesto mensual (RN-005).
- RF-005: Cálculo de balance mensual (ingresos, gastos, saldo neto).
- RF-006: Desglose de consumo presupuestario por categoría.
- RF-007: Listado filtrable de transacciones.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, List, Optional, Tuple

from src.domain.exceptions import CategoriaInvalidaError
from src.domain.models import Categoria, TipoTransaccion, Transaccion
from src.persistence.repository import RepositorioFinanzas


@dataclass
class ResumenCategoria:
    """Estructura de datos para el reporte de consumo de una categoría."""
    categoria_nombre: str
    presupuesto: Decimal
    gasto_acumulado: Decimal
    porcentaje_consumido: Decimal
    estado: str  # 'NORMAL', 'ALERTA' o 'EXCEDIDO'


@dataclass
class BalanceMensual:
    """Estructura del balance financiero de un mes determinado."""
    anio: int
    mes: int
    total_ingresos: Decimal
    total_gastos: Decimal
    saldo_neto: Decimal
    resumen_categorias: List[ResumenCategoria]


class ServicioFinanzas:
    """Orquestador de lógica de negocio y casos de uso financieros."""

    def __init__(self, repositorio: RepositorioFinanzas) -> None:
        self.repo = repositorio

    # ==========================================
    # CASO DE USO 1: GESTIÓN DE CATEGORÍAS
    # ==========================================

    def registrar_categoria(self, nombre: str, presupuesto_mensual: Any) -> Categoria:
        """Crea o actualiza una categoría en el sistema."""
        cat_existente = self.repo.obtener_categoria(nombre)
        if cat_existente:
            cat_existente.actualizar_presupuesto(presupuesto_mensual)
            self.repo.guardar_categoria(cat_existente)
            return cat_existente

        nueva_cat = Categoria(nombre=nombre, presupuesto_mensual=presupuesto_mensual)
        self.repo.guardar_categoria(nueva_cat)
        return nueva_cat

    def listar_categorias(self) -> List[Categoria]:
        """Retorna todas las categorías registradas."""
        return self.repo.obtener_todas_las_categorias()

    # ==========================================
    # CASO DE USO 2: REGISTRO DE TRANSACCIÓN Y ALERTAS
    # ==========================================

    def registrar_transaccion(
        self,
        tipo: TipoTransaccion | str,
        monto: Any,
        categoria_nombre: str,
        descripcion: str = "",
        fecha: Optional[date] = None,
    ) -> Tuple[Transaccion, Optional[str]]:
        """Registra una transacción verificando reglas de negocio y presupuestos.

        Retorna:
            Tupla con la transacción guardada y un mensaje de advertencia (si aplica).
        """
        # Regla RN-003: La categoría debe existir previamente en el sistema
        categoria = self.repo.obtener_categoria(categoria_nombre)
        if not categoria:
            raise CategoriaInvalidaError(
                f"La categoría '{categoria_nombre}' no existe. Debe registrarla primero."
            )

        # Crear y persistir la transacción
        transaccion = Transaccion(
            tipo=tipo,
            monto=monto,
            categoria_nombre=categoria.nombre,
            descripcion=descripcion,
            fecha=fecha if fecha else date.today(),
        )
        self.repo.guardar_transaccion(transaccion)

        # Regla RN-005 y RF-004: Verificar consumo del presupuesto si es un gasto
        alerta = None
        if transaccion.tipo == TipoTransaccion.GASTO:
            alerta = self._evaluar_alerta_presupuesto(transaccion, categoria)

        return transaccion, alerta

    def _evaluar_alerta_presupuesto(
        self, tx: Transaccion, categoria: Categoria
    ) -> Optional[str]:
        """Calcula si el gasto acumulado en el mes sobrepasa el presupuesto de la categoría."""
        # Filtrar gastos de este mismo mes, año y categoría
        gastos_mes = [
            t.monto
            for t in self.repo.obtener_todas_las_transacciones()
            if t.tipo == TipoTransaccion.GASTO
            and t.categoria_nombre == categoria.nombre
            and t.fecha.year == tx.fecha.year
            and t.fecha.month == tx.fecha.month
        ]
        total_gastado = sum(gastos_mes, Decimal("0.00"))

        # Porcentaje consumido
        porcentaje = (total_gastado / categoria.presupuesto_mensual) * Decimal("100")

        if total_gastado > categoria.presupuesto_mensual:
            exceso = total_gastado - categoria.presupuesto_mensual
            return (
                f"⚠️ ALERTA: Has excedido el presupuesto de '{categoria.nombre}' "
                f"en ${exceso:.2f} ({porcentaje:.1f}% consumido)."
            )
        elif porcentaje >= Decimal("80.0"):
            return (
                f"ℹ️ AVISO: Has consumido el {porcentaje:.1f}% del presupuesto "
                f"de '{categoria.nombre}' para este mes."
            )
        return None

    # ==========================================
    # CASO DE USO 3: BALANCE Y REPORTES MENSUALES
    # ==========================================

    def obtener_balance_mensual(self, anio: int, mes: int) -> BalanceMensual:
        """Calcula el balance general de un mes y el desglose de categorías."""
        todas = self.repo.obtener_todas_las_transacciones()
        # Filtrar por año y mes
        tx_mes = [t for t in todas if t.fecha.year == anio and t.fecha.month == mes]

        total_ingresos = sum(
            (t.monto for t in tx_mes if t.tipo == TipoTransaccion.INGRESO),
            Decimal("0.00"),
        )
        total_gastos = sum(
            (t.monto for t in tx_mes if t.tipo == TipoTransaccion.GASTO),
            Decimal("0.00"),
        )
        saldo_neto = total_ingresos - total_gastos

        # Desglose por categoría
        resumenes: List[ResumenCategoria] = []
        for cat in self.repo.obtener_todas_las_categorias():
            gastos_cat = sum(
                (
                    t.monto
                    for t in tx_mes
                    if t.tipo == TipoTransaccion.GASTO
                    and t.categoria_nombre == cat.nombre
                ),
                Decimal("0.00"),
            )
            porcentaje = (gastos_cat / cat.presupuesto_mensual) * Decimal("100")

            if gastos_cat > cat.presupuesto_mensual:
                estado = "EXCEDIDO"
            elif porcentaje >= Decimal("80.0"):
                estado = "ALERTA"
            else:
                estado = "NORMAL"

            resumenes.append(
                ResumenCategoria(
                    categoria_nombre=cat.nombre,
                    presupuesto=cat.presupuesto_mensual,
                    gasto_acumulado=gastos_cat,
                    porcentaje_consumido=porcentaje.quantize(Decimal("0.1")),
                    estado=estado,
                )
            )

        return BalanceMensual(
            anio=anio,
            mes=mes,
            total_ingresos=total_ingresos,
            total_gastos=total_gastos,
            saldo_neto=saldo_neto,
            resumen_categorias=resumenes,
        )

    # ==========================================
    # CASO DE USO 4: LISTAR Y FILTRAR
    # ==========================================

    def listar_transacciones(
        self,
        anio: Optional[int] = None,
        mes: Optional[int] = None,
        categoria_nombre: Optional[str] = None,
    ) -> List[Transaccion]:
        """Retorna transacciones con filtros opcionales de fecha y categoría."""
        lista = self.repo.obtener_todas_las_transacciones()

        if anio is not None:
            lista = [t for t in lista if t.fecha.year == anio]
        if mes is not None:
            lista = [t for t in lista if t.fecha.month == mes]
        if categoria_nombre is not None:
            nombre_norm = categoria_nombre.strip().capitalize()
            lista = [t for t in lista if t.categoria_nombre == nombre_norm]

        # Ordenar cronológicamente (más recientes primero)
        return sorted(lista, key=lambda t: t.fecha, reverse=True)
