"""Punto de entrada principal del Gestor de Finanzas Personales.

Aplica el principio de Inversión de Control (IoC):
Conecta las capas de Persistencia, Servicios y Presentación (CLI).
"""

from src.cli.console_app import AppFinanzasCLI
from src.persistence.repository import RepositorioFinanzas
from src.services.finance_service import ServicioFinanzas


def main() -> None:
    """Inicializa dependencias y arranca la aplicación."""
    # 1. Capa de persistencia (archivo por defecto en data/finanzas.json)
    repositorio = RepositorioFinanzas()

    # 2. Capa de servicios (inyección de dependencias)
    servicio = ServicioFinanzas(repositorio=repositorio)

    # 3. Capa de presentación (interfaz de usuario)
    app = AppFinanzasCLI(servicio=servicio)

    # 4. Iniciar bucle interactivo
    app.iniciar()


if __name__ == "__main__":
    main()
