"""Jerarquía de excepciones del dominio financiero

Permite que las capas superiores (servicios, interfaz) capturen errores de negocio especificos sin acoplarse a detalles tecnicos ni propagar errores genericos no controlados
"""

class FinanzasError(Exception):
    """Excepcion base para todos los errores de la aplicacion de finanzas"""
    pass

class MontoInvalidoError(FinanzasError):
    """Lanzada cuando un monto no cumple la regla de positividad (>0)"""
    pass

class CategoriaInvalidaError(FinanzasError):
    """Lanzada cuando una categoria no es valida o no existe"""
    pass

class FechaInvalidaError(FinanzasError):
    """Lanzada cuando una fecha no cumple con los limites de negocio aceptables"""
    pass

class OperacionInvalidaError(FinanzasError):
    """Lanzada cuando una operacion viola una regla de flujo de negocio"""
    pass
