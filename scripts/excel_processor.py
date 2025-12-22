"""
LexNum - Excel Processing Utilities
====================================

Functions for processing Excel files and finding data columns.

Autor: Omar Gabriel Salvatierra Garcia
Organización: Órgano de Fiscalización Superior del Estado de Tlaxcala
"""

import re
import unicodedata
from typing import Optional, Any

import pandas as pd


# =========================================================
# CONSTANTES
# =========================================================
COLUMN_ALIASES = frozenset({"numero", "num"})


# =========================================================
# FUNCIONES DE NORMALIZACIÓN
# =========================================================
def normalize(text: Any) -> str:
    """
    Normaliza texto eliminando acentos, espacios y convirtiendo a minúsculas.

    Args:
        text: Texto a normalizar (cualquier tipo, se convertirá a string)

    Returns:
        str: Texto normalizado en minúsculas sin acentos ni espacios

    Example:
        >>> normalize("Número")
        'numero'
        >>> normalize("  Num  ")
        'num'
    """
    text_str = str(text)
    # Normalizar caracteres Unicode (remover acentos)
    normalized = unicodedata.normalize("NFKD", text_str)
    # Filtrar caracteres combinantes (acentos)
    without_accents = "".join(
        char for char in normalized
        if not unicodedata.combining(char)
    )
    # Remover espacios y convertir a minúsculas
    return re.sub(r"\s+", "", without_accents).lower()


def find_num_column(df: pd.DataFrame) -> Optional[str]:
    """
    Encuentra la columna de números en un DataFrame de pandas.

    Busca columnas con nombres que coincidan con variaciones de
    'Número' o 'Num' (insensible a acentos, mayúsculas y espacios).

    Args:
        df: DataFrame de pandas donde buscar la columna

    Returns:
        str | None: Nombre exacto de la columna encontrada, o None si no existe

    Example:
        >>> df = pd.DataFrame({"Número": [1, 2, 3]})
        >>> find_num_column(df)
        'Número'
    """
    for column in df.columns:
        if normalize(column) in COLUMN_ALIASES:
            return column
    return None
