"""Módulo de persistencia atómica en formato JSON.

Implementa el patrón Repositorio y garantiza el requisito RNF-001 (Confiabilidad):
la base de datos jamás quedará corrupta ante apagones o interrupciones.
"""

from decimal import Decimal
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from src.domain.models import Categoria, Transaccion


class RepositorioFinanzas:
    """Gestiona el almacenamiento y recuperación de datos financieros en un archivo JSON."""

    def __init__(self, ruta_archivo: Path | str = "data/finanzas.json") -> None:
        self.ruta_archivo = Path(ruta_archivo)
        # Asegura que la carpeta contenedora (ej. 'data/') exista
        self.ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
        self._asegurar_archivo_inicial()

    def _asegurar_archivo_inicial(self) -> None:
        """Si el archivo no existe, lo inicializa con estructura JSON vacía."""
        if not self.ruta_archivo.exists():
            datos_iniciales = {
                "categorias": {},
                "transacciones": []
            }
            self._guardar_datos_atomicamente(datos_iniciales)

    def _leer_datos(self) -> Dict:
        """Lee y deserializa el contenido completo del archivo JSON con blindaje de esquema."""
        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except (json.JSONDecodeError, FileNotFoundError):
            datos = {"categorias": {}, "transacciones": []}

        # Blindaje: Si alguien alteró el JSON dejándolo como lista u otro tipo no-dict
        if not isinstance(datos, dict):
            datos = {}
        datos.setdefault("categorias", {})
        datos.setdefault("transacciones", [])
        return datos

    def _guardar_datos_atomicamente(self, datos: Dict) -> None:
        """Guarda los datos utilizando el patrón de reemplazo atómico."""
        # 1. Crear un archivo temporal en la misma carpeta
        ruta_temporal = self.ruta_archivo.with_suffix(".tmp")

        # 2. Escribir en el archivo temporal
        with open(ruta_temporal, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=2, ensure_ascii=False)
            archivo.flush()             # Vacia los buffers de Python al sistema
            os.fsync(archivo.fileno())   # Obliga al sistema operativo a grabar en el disco físico

        # 3. Reemplazar atómicamente el temporal por el archivo final
        os.replace(ruta_temporal, self.ruta_archivo)

    # ==========================================
    # MÉTODOS PÚBLICOS PARA CATEGORÍAS
    # ==========================================

    def guardar_categoria(self, categoria: Categoria) -> None:
        """Guarda o actualiza una categoría por su nombre."""
        datos = self._leer_datos()
        datos["categorias"][categoria.nombre] = categoria.to_dict()
        self._guardar_datos_atomicamente(datos)

    def obtener_categoria(self, nombre: str) -> Optional[Categoria]:
        """Busca una categoría por nombre normalizado. Retorna None si no existe."""
        datos = self._leer_datos()
        nombre_normalizado = nombre.strip().capitalize()
        cat_dict = datos["categorias"].get(nombre_normalizado)
        if cat_dict:
            return Categoria.from_dict(cat_dict)
        return None

    def obtener_todas_las_categorias(self) -> List[Categoria]:
        """Retorna la lista de todas las categorías registradas."""
        datos = self._leer_datos()
        return [Categoria.from_dict(d) for d in datos["categorias"].values()]

    # ==========================================
    # MÉTODOS PÚBLICOS PARA TRANSACCIONES
    # ==========================================

    def guardar_transaccion(self, transaccion: Transaccion) -> None:
        """Agrega una nueva transacción al registro persistente."""
        datos = self._leer_datos()
        datos["transacciones"].append(transaccion.to_dict())
        self._guardar_datos_atomicamente(datos)

    def obtener_todas_las_transacciones(self) -> List[Transaccion]:
        """Retorna todas las transacciones históricas registradas."""
        datos = self._leer_datos()
        return [Transaccion.from_dict(d) for d in datos["transacciones"]]
