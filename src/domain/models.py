"""Modelos del dominio financiero.

Implementan las reglas de negocio puras (RN-001 a RN-004):
- Precisión monetaria exacta mediante Decimal.
- Inmutabilidad de identificadores (UUID).
- Validación de datos en el momento de instanciación.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any, Dict
import uuid

from .exceptions import CategoriaInvalidaError, FechaInvalidaError, MontoInvalidoError


class TipoTransaccion(str, Enum):
    """Tipo de movimiento financiero permitido."""
    INGRESO = "INGRESO"
    GASTO = "GASTO"


def _parsear_decimal(valor: Any, nombre_campo: str = "monto") -> Decimal:
    """Función auxiliar: convierte de forma segura cualquier entrada a Decimal positivo (> 0).

    Aplica la Regla de Negocio RN-001 (Positividad Monetaria).
    """
    try:
        if isinstance(valor, float):
            decimal_val = Decimal(str(valor))
        else:
            decimal_val = Decimal(valor)
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise MontoInvalidoError(
            f"El valor de '{nombre_campo}' debe ser un número válido: {valor}"
        ) from exc

    if decimal_val <= Decimal("0.00"):
        raise MontoInvalidoError(
            f"El '{nombre_campo}' debe ser mayor a 0.00. Valor recibido: {decimal_val}"
        )

    # Fijamos siempre 2 decimales exactos (ej. 15.50)
    return decimal_val.quantize(Decimal("0.01"))


@dataclass
class Categoria:
    """Entidad que representa una categoría y su tope presupuestario mensual."""

    nombre: str
    presupuesto_mensual: Decimal
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self) -> None:
        # Validación de nombre (no vacío)
        if not self.nombre or not self.nombre.strip():
            raise CategoriaInvalidaError("El nombre de la categoría no puede estar vacío.")
        self.nombre = self.nombre.strip().capitalize()

        # Validación del presupuesto mensual
        self.presupuesto_mensual = _parsear_decimal(
            self.presupuesto_mensual, nombre_campo="presupuesto_mensual"
        )

    def actualizar_presupuesto(self, nuevo_monto: Any) -> None:
        """Permite modificar el presupuesto validando el nuevo valor."""
        self.presupuesto_mensual = _parsear_decimal(
            nuevo_monto, nombre_campo="presupuesto_mensual"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la categoría a un diccionario listo para serializar a JSON."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "presupuesto_mensual": str(self.presupuesto_mensual),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Categoria":
        """Reconstruye una instancia de Categoria a partir de un diccionario."""
        return cls(
            id=data["id"],
            nombre=data["nombre"],
            presupuesto_mensual=Decimal(data["presupuesto_mensual"]),
        )


@dataclass
class Transaccion:
    """Entidad que representa un movimiento financiero individual."""

    tipo: TipoTransaccion
    monto: Decimal
    categoria_nombre: str
    descripcion: str = ""
    fecha: date = field(default_factory=date.today)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self) -> None:
        # 1. Validar y normalizar el tipo
        if isinstance(self.tipo, str):
            try:
                self.tipo = TipoTransaccion(self.tipo.upper())
            except ValueError as exc:
                raise MontoInvalidoError(
                    f"Tipo de transacción inválido: '{self.tipo}'. Use INGRESO o GASTO."
                ) from exc

        # 2. Validar y normalizar el monto positivo
        self.monto = _parsear_decimal(self.monto, nombre_campo="monto")

        # 3. Validar categoría asignada
        if not self.categoria_nombre or not self.categoria_nombre.strip():
            raise CategoriaInvalidaError("Toda transacción debe tener una categoría.")
        self.categoria_nombre = self.categoria_nombre.strip().capitalize()

        # 4. Limpiar descripción
        self.descripcion = self.descripcion.strip() if self.descripcion else ""

        # 5. Validar fecha (Regla RN-004)
        if isinstance(self.fecha, str):
            try:
                self.fecha = date.fromisoformat(self.fecha)
            except ValueError as exc:
                raise FechaInvalidaError(
                    f"Formato de fecha inválido '{self.fecha}'. Use YYYY-MM-DD."
                ) from exc

        hoy = date.today()
        limite_futuro = hoy + timedelta(days=1)
        limite_pasado = hoy - timedelta(days=365 * 5)

        if self.fecha > limite_futuro:
            raise FechaInvalidaError(
                f"La fecha ({self.fecha}) no puede ser futura respecto al día de hoy."
            )

        if self.fecha < limite_pasado:
            raise FechaInvalidaError(
                f"La fecha ({self.fecha}) no puede ser anterior a 5 años atrás."
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la transacción a un diccionario listo para JSON."""
        return {
            "id": self.id,
            "tipo": self.tipo.value,
            "monto": str(self.monto),
            "categoria_nombre": self.categoria_nombre,
            "descripcion": self.descripcion,
            "fecha": self.fecha.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transaccion":
        """Reconstruye una transacción a partir de un diccionario."""
        return cls(
            id=data["id"],
            tipo=TipoTransaccion(data["tipo"]),
            monto=Decimal(data["monto"]),
            categoria_nombre=data["categoria_nombre"],
            descripcion=data.get("descripcion", ""),
            fecha=date.fromisoformat(data["fecha"]),
        )
