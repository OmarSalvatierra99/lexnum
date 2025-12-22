"""
LexNum - Aplicación Web para Conversión Numérica a Texto Monetario
====================================================================

Aplicación Flask que convierte números a su representación en texto
en formato monetario mexicano oficial para uso institucional.

Autor: Omar Gabriel Salvatierra Garcia
Organización: Órgano de Fiscalización Superior del Estado de Tlaxcala
"""

import logging
from io import BytesIO
from pathlib import Path
from typing import Tuple, Dict, Any
from logging.handlers import RotatingFileHandler

import pandas as pd
from flask import Flask, render_template, request, send_file, jsonify, Response
from werkzeug.exceptions import RequestEntityTooLarge

from config import Config
from scripts.converter import numero_a_texto
from scripts.excel_processor import find_num_column
from scripts.validators import validate_file


# =========================================================
# INICIALIZACIÓN DE FLASK
# =========================================================
app = Flask(__name__)
app.config.from_object(Config)


# =========================================================
# CONFIGURACIÓN DE LOGGING
# =========================================================
Config.LOG_DIR.mkdir(exist_ok=True)
file_handler = RotatingFileHandler(
    Config.LOG_FILE,
    maxBytes=Config.LOG_MAX_BYTES,
    backupCount=Config.LOG_BACKUP_COUNT
)
file_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
file_handler.setFormatter(logging.Formatter(Config.LOG_FORMAT))

console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
console_handler.setFormatter(logging.Formatter(Config.LOG_FORMAT))

app.logger.addHandler(file_handler)
app.logger.addHandler(console_handler)
app.logger.setLevel(getattr(logging, Config.LOG_LEVEL))
app.logger.info("LexNum iniciado correctamente")


# =========================================================
# RUTAS
# =========================================================
@app.route("/")
def index() -> str:
    """Renderiza la página principal."""
    return render_template("index.html")


@app.route("/health")
def health() -> Tuple[Dict[str, str], int]:
    """Endpoint de salud para monitoreo."""
    return jsonify({"status": "healthy", "service": "LexNum"}), 200


@app.route("/convertir_texto", methods=["POST"])
def convertir_texto() -> Tuple[Dict[str, Any], int]:
    """
    Convierte un número individual a texto monetario.

    Returns:
        JSON con el texto convertido o error
    """
    try:
        data = request.get_json(silent=True) or {}
        numero = data.get("numero", "")

        if not numero:
            return jsonify({"texto": ""}), 200

        texto = numero_a_texto(numero)
        app.logger.debug(f"Conversión: {numero} -> {texto}")

        return jsonify({"texto": texto}), 200

    except Exception as e:
        app.logger.error(f"Error en convertir_texto: {e}")
        return jsonify({
            "error": Config.ERROR_CONVERSION
        }), 500


@app.route("/convertir_excel", methods=["POST"])
def convertir_excel() -> Tuple[Response, int]:
    """
    Procesa un archivo Excel y retorna el resultado con conversiones.

    Returns:
        Archivo Excel con columna de texto agregada o error JSON
    """
    try:
        # Validar que se subió un archivo
        archivo = request.files.get("archivo")
        if not archivo:
            return jsonify({
                "error": Config.ERROR_NO_FILE
            }), 400

        # Validar el archivo
        is_valid, error_message = validate_file(archivo)
        if not is_valid:
            return jsonify({"error": error_message}), 400

        # Leer Excel
        try:
            df = pd.read_excel(archivo)
            app.logger.info(f"Excel leído: {len(df)} filas")
        except Exception as e:
            app.logger.error(f"Error leyendo Excel: {e}")
            return jsonify({
                "error": Config.ERROR_INVALID_EXCEL
            }), 400

        # Encontrar columna de números
        col = find_num_column(df)
        if not col:
            return jsonify({
                "error": Config.ERROR_NO_COLUMN
            }), 400

        # Aplicar conversión
        df["Texto"] = df[col].apply(numero_a_texto)
        app.logger.info(f"Conversiones aplicadas en columna: {col}")

        # Generar archivo Excel en memoria
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        buf.seek(0)

        # Enviar archivo
        return send_file(
            buf,
            as_attachment=True,
            download_name=Config.OUTPUT_FILENAME,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ), 200

    except Exception as e:
        app.logger.error(f"Error en convertir_excel: {e}")
        return jsonify({
            "error": "Error interno del servidor."
        }), 500


# =========================================================
# MANEJADORES DE ERRORES
# =========================================================
@app.errorhandler(413)
@app.errorhandler(RequestEntityTooLarge)
def handle_large_file(e):
    """Maneja archivos que exceden el tamaño máximo."""
    max_size = Config.MAX_FILE_SIZE_MB
    return jsonify({
        "error": f"El archivo excede el tamaño máximo permitido de {max_size} MB."
    }), 413


@app.errorhandler(404)
def handle_not_found(e):
    """Maneja rutas no encontradas."""
    return jsonify({"error": "Ruta no encontrada."}), 404


@app.errorhandler(500)
def handle_internal_error(e):
    """Maneja errores internos del servidor."""
    app.logger.error(f"Error interno: {e}")
    return jsonify({"error": "Error interno del servidor."}), 500


# =========================================================
# SECURITY HEADERS
# =========================================================
@app.after_request
def add_security_headers(response: Response) -> Response:
    """Agrega encabezados de seguridad a todas las respuestas."""
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


# =========================================================
# PUNTO DE ENTRADA
# =========================================================
if __name__ == "__main__":
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
