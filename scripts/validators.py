"""
LexNum - Input Validation Functions
====================================

Validation functions for file uploads and user input.

Autor: Omar Gabriel Salvatierra Garcia
Organización: Órgano de Fiscalización Superior del Estado de Tlaxcala
"""

from typing import Tuple
from werkzeug.datastructures import FileStorage


def validate_file(file: FileStorage) -> Tuple[bool, str]:
    """
    Valida que el archivo subido sea válido.

    Args:
        file: Archivo subido por el usuario

    Returns:
        Tuple[bool, str]: (es_válido, mensaje_error)

    Example:
        >>> from werkzeug.datastructures import FileStorage
        >>> file = FileStorage(filename="test.xlsx")
        >>> is_valid, error = validate_file(file)
        >>> is_valid
        True
    """
    if not file or file.filename == "":
        return False, "No se proporcionó ningún archivo."

    # Validar extensión
    if not file.filename or "." not in file.filename:
        return False, "El archivo debe tener una extensión válida."

    extension = file.filename.rsplit(".", 1)[1].lower()
    if extension not in {"xlsx", "xls"}:
        return False, "Solo se permiten archivos Excel (.xlsx, .xls)."

    return True, ""
