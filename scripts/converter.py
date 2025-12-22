"""
LexNum - Number to Text Conversion
===================================

Functions for converting numbers to monetary text format.

Autor: Omar Gabriel Salvatierra Garcia
Organización: Órgano de Fiscalización Superior del Estado de Tlaxcala
"""

import re
import unicodedata
from typing import Optional, Any

from num2words import num2words


# =========================================================
# CONSTANTES
# =========================================================
CURRENCY_SYMBOLS = ("$", "MXN", "M.N.", "MN", ",")
DECIMAL_PRECISION = 100
CURRENCY_SUFFIX = "M.N."


# =========================================================
# FUNCIONES DE LIMPIEZA Y CONVERSIÓN
# =========================================================
def clean_num(value: Any) -> Optional[float]:
    """
    Limpia y convierte un valor a número flotante.

    Remueve símbolos de moneda, comas y espacios, luego convierte
    a float. Retorna None si el valor es vacío o inválido.

    Args:
        value: Valor a limpiar (string, número, etc.)

    Returns:
        float | None: Número flotante limpio o None si es inválido

    Raises:
        ValueError: Si el valor no puede convertirse a número

    Example:
        >>> clean_num("$1,234.56")
        1234.56
        >>> clean_num("")
        None
    """
    # Validar valores vacíos o None
    if value in (None, "", " "):
        return None

    # Convertir a string y limpiar símbolos
    value_str = str(value).strip()

    # Remover símbolos de moneda y separadores
    for symbol in CURRENCY_SYMBOLS:
        value_str = value_str.replace(symbol, "")

    value_str = value_str.strip()

    # Validar que no esté vacío después de limpiar
    if not value_str:
        return None

    # Convertir a float
    try:
        return float(value_str)
    except ValueError as e:
        raise ValueError(f"No se pudo convertir '{value}' a número: {e}")


def numero_a_texto(valor: Any) -> str:
    """
    Convierte un número a su representación en texto monetario mexicano.

    Convierte valores numéricos a formato oficial de texto monetario,
    por ejemplo: 1523.45 → "MIL QUINIENTOS VEINTITRÉS PESOS 45/100 M.N."

    Args:
        valor: Valor numérico a convertir (int, float, string, etc.)

    Returns:
        str: Representación en texto del valor monetario, o string vacío si hay error

    Example:
        >>> numero_a_texto(1523.45)
        'MIL QUINIENTOS VEINTITRÉS PESOS 45/100 M.N.'
        >>> numero_a_texto(1)
        'UN PESO 00/100 M.N.'
        >>> numero_a_texto(0)
        'CERO PESOS 00/100 M.N.'
    """
    try:
        # Limpiar y validar el número
        numero = clean_num(valor)

        if numero is None:
            return ""

        # Separar parte entera y decimal
        parte_entera = int(numero)
        parte_decimal = round((numero - parte_entera) * DECIMAL_PRECISION)

        # Convertir parte entera a texto
        texto_numero = num2words(parte_entera, lang="es").upper()

        # Normalizar "UNO" a "UN" según reglas gramaticales
        texto_numero = (
            texto_numero
            .replace(" UNO ", " UN ")
            .replace("UNO ", "UN ")
            .replace(" UNO", " UN")
        )

        # Construir sufijo con centavos
        sufijo_centavos = f"{parte_decimal:02d}/100 {CURRENCY_SUFFIX}"

        # Caso especial: un peso
        if parte_entera == 1:
            return f"UN PESO {sufijo_centavos}"

        # Caso general: múltiples pesos o cero
        return f"{texto_numero} PESOS {sufijo_centavos}"

    except (ValueError, TypeError, AttributeError) as e:
        # En caso de error, retornar string vacío
        return ""
