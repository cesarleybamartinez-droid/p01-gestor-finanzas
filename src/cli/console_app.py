"""Interfaz de línea de comandos (CLI) interactiva para el Gestor de Finanzas.

Aplica el requisito RNF-004 (Usabilidad):
- Menús claros y organizados.
- Captura de errores defensiva sin tracebacks crudos de Python.
- Confirmación visual de operaciones y alertas de presupuesto.
"""

from datetime import date
from decimal import Decimal
import sys
from typing import Optional

from src.domain.exceptions import FinanzasError
from src.domain.models import TipoTransaccion
from src.services.finance_service import ServicioFinanzas


class AppFinanzasCLI:
    """Controlador de la interfaz de consola interactiva."""

    def __init__(self, servicio: ServicioFinanzas) -> None:
        self.servicio = servicio

    def iniciar(self) -> None:
        """Bucle principal de la aplicación de terminal."""
        while True:
            try:
                self._mostrar_menu_principal()
                opcion = input("\n👉 Selecciona una opción [1-5]: ").strip()

                if opcion == "1":
                    self._menu_registrar_transaccion()
                elif opcion == "2":
                    self._menu_gestionar_categoria()
                elif opcion == "3":
                    self._menu_ver_balance_mensual()
                elif opcion == "4":
                    self._menu_listar_transacciones()
                elif opcion == "5":
                    print("\n👋 ¡Gracias por usar el Gestor de Finanzas! Tus datos están a salvo.")
                    sys.exit(0)
                else:
                    print("❌ Opción inválida. Por favor ingresa un número del 1 al 5.")

                input("\nPresiona ENTER para continuar...")
            except KeyboardInterrupt:
                print("\n\n👋 Operación cancelada por el usuario. ¡Hasta luego!")
                sys.exit(0)

    def _mostrar_menu_principal(self) -> None:
        """Imprime la cabecera del menú."""
        print("\n" + "=" * 60)
        print("          💰 GESTOR DE FINANZAS PERSONALES v1.0")
        print("=" * 60)
        print("  [1] 💵 Registrar Transacción (Ingreso o Gasto)")
        print("  [2] 🏷️  Crear o Modificar Categoría y Presupuesto")
        print("  [3] 📊 Ver Balance Mensual y Desglose de Gastos")
        print("  [4] 📜 Listar Historial de Movimientos")
        print("  [5] 🚪 Salir")
        print("=" * 60)

    # ==========================================
    # OPCIÓN 1: REGISTRAR TRANSACCIÓN
    # ==========================================

    def _menu_registrar_transaccion(self) -> None:
        print("\n--- 💵 REGISTRAR MOVIMIENTO ---")
        try:
            # 1. Tipo
            tipo_input = input("¿Es [1] GASTO o [2] INGRESO? [1/2]: ").strip()
            if tipo_input == "1":
                tipo = TipoTransaccion.GASTO
            elif tipo_input == "2":
                tipo = TipoTransaccion.INGRESO
            else:
                print("❌ Opción inválida. Debe ser 1 o 2.")
                return

            # 2. Categorías disponibles
            categorias = self.servicio.listar_categorias()
            if not categorias:
                print("⚠️ AVISO: No tienes categorías creadas aún.")
                print("Crea al menos una categoría (Opción 2 del menú) antes de registrar movimientos.")
                return

            print("Categorías disponibles:", ", ".join(c.nombre for c in categorias))
            categoria = input("Nombre de la categoría: ").strip()

            # 3. Monto
            monto = input("Monto: $").strip()

            # 4. Descripción
            descripcion = input("Descripción (opcional): ").strip()

            # 5. Fecha
            fecha_str = input("Fecha YYYY-MM-DD (ENTER para fecha de hoy): ").strip()
            fecha = date.fromisoformat(fecha_str) if fecha_str else date.today()

            # Guardar mediante el servicio
            tx, alerta = self.servicio.registrar_transaccion(
                tipo=tipo,
                monto=monto,
                categoria_nombre=categoria,
                descripcion=descripcion,
                fecha=fecha,
            )

            print(f"\n✅ {tx.tipo.value} registrado con éxito:")
            print(f"   ID: {tx.id[:8]}... | Fecha: {tx.fecha} | Monto: ${tx.monto:.2f} | Categoría: {tx.categoria_nombre}")

            # Mostrar alerta de presupuesto si se excedió (RF-004)
            if alerta:
                print(f"\n{alerta}")

        except FinanzasError as error:
            print(f"\n❌ Error de validación: {error}")
        except ValueError:
            print("\n❌ Error: Formato de fecha inválido. Debe ser YYYY-MM-DD.")

    # ==========================================
    # OPCIÓN 2: GESTIONAR CATEGORÍA
    # ==========================================

    def _menu_gestionar_categoria(self) -> None:
        print("\n--- 🏷️  CREAR O MODIFICAR CATEGORÍA ---")
        try:
            nombre = input("Nombre de la categoría (ej. Alimentación, Sueldo): ").strip()
            presupuesto = input("Tope presupuestario mensual para esta categoría: $").strip()

            cat = self.servicio.registrar_categoria(
                nombre=nombre, presupuesto_mensual=presupuesto
            )
            print(f"\n✅ Categoría '{cat.nombre}' guardada con éxito.")
            print(f"   Presupuesto Mensual Asignado: ${cat.presupuesto_mensual:.2f}")

        except FinanzasError as error:
            print(f"\n❌ Error: {error}")

    # ==========================================
    # OPCIÓN 3: BALANCE MENSUAL Y REPORTES
    # ==========================================

    def _menu_ver_balance_mensual(self) -> None:
        print("\n--- 📊 BALANCE MENSUAL ---")
        try:
            hoy = date.today()
            anio_input = input(f"Año [{hoy.year}]: ").strip()
            mes_input = input(f"Mes (1-12) [{hoy.month}]: ").strip()

            anio = int(anio_input) if anio_input else hoy.year
            mes = int(mes_input) if mes_input else hoy.month

            if mes < 1 or mes > 12:
                print("❌ El mes debe estar entre 1 y 12.")
                return

            balance = self.servicio.obtener_balance_mensual(anio=anio, mes=mes)

            print("\n" + "=" * 65)
            print(f"             RESUMEN FINANCIERO: {mes:02d} / {anio}")
            print("=" * 65)
            print(f"  (+) Total Ingresos : ${balance.total_ingresos:>10.2f}")
            print(f"  (-) Total Gastos   : ${balance.total_gastos:>10.2f}")
            print("  " + "-" * 35)
            print(f"  (=) Saldo Neto     : ${balance.saldo_neto:>10.2f}")
            print("=" * 65)

            print("\n📌 DESGLOSE DE PRESUPUESTO POR CATEGORÍA:")
            print(f"{'Categoría':<18} | {'Presupuesto':<12} | {'Gastado':<10} | {'% Usado':<8} | Estado")
            print("-" * 65)

            if not balance.resumen_categorias:
                print("  (No hay categorías registradas en el sistema)")
            else:
                for r in balance.resumen_categorias:
                    icono = "🟢" if r.estado == "NORMAL" else ("🟡" if r.estado == "ALERTA" else "🔴")
                    print(
                        f"{r.categoria_nombre:<18} | "
                        f"${r.presupuesto:>10.2f} | "
                        f"${r.gasto_acumulado:>8.2f} | "
                        f"{r.porcentaje_consumido:>6.1f}% | "
                        f"{icono} {r.estado}"
                    )

        except ValueError:
            print("❌ Entrada inválida. El año y mes deben ser números enteros.")

    # ==========================================
    # OPCIÓN 4: LISTAR MOVIMIENTOS
    # ==========================================

    def _menu_listar_transacciones(self) -> None:
        print("\n--- 📜 HISTORIAL DE MOVIMIENTOS ---")
        filtro_mes = input("Filtrar por mes (1-12 o ENTER para todos): ").strip()
        filtro_cat = input("Filtrar por categoría (o ENTER para todas): ").strip()

        mes = int(filtro_mes) if filtro_mes.isdigit() else None
        categoria = filtro_cat if filtro_cat else None

        transacciones = self.servicio.listar_transacciones(
            mes=mes, categoria_nombre=categoria
        )

        if not transacciones:
            print("\nℹ️ No se encontraron movimientos con los filtros especificados.")
            return

        print("\n" + "=" * 70)
        print(f"{'Fecha':<12} | {'Tipo':<8} | {'Categoría':<15} | {'Monto':<10} | Descripción")
        print("=" * 70)
        for t in transacciones:
            signo = "+" if t.tipo == TipoTransaccion.INGRESO else "-"
            monto_str = f"{signo}${t.monto:.2f}"
            print(f"{t.fecha.isoformat():<12} | {t.tipo.value:<8} | {t.categoria_nombre:<15} | {monto_str:>10} | {t.descripcion}")
        print("=" * 70)
