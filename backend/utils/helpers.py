"""
helpers.py - Funciones auxiliares.
Utilidades generales que se usan en varias partes del backend.
"""

from functools import wraps
from flask import jsonify, session


def respuesta_ok(data=None):
    """
    Devuelve una respuesta JSON exitosa.
    Siempre incluye ok=True más los datos que le pasemos.
    Ejemplo: {"ok": True, "user": {...}}
    """
    respuesta = {"ok": True}
    # Si nos pasan un diccionario, lo añadimos a la respuesta
    if data:
        respuesta.update(data)
    return jsonify(respuesta)


def respuesta_error(mensaje, codigo=400):
    """
    Devuelve una respuesta JSON de error.
    Incluye ok=False y el mensaje de error.
    Ejemplo: {"ok": False, "error": "El usuario ya existe"}
    """
    return jsonify({"ok": False, "error": mensaje}), codigo


def login_requerido(f):
    """
    Decorador que protege una ruta.
    Verifica que el usuario haya iniciado sesión (que exista user_id en la sesión).
    Si no está logueado, devuelve error 401 (no autorizado).

    Uso:
        @app.route("/ruta-protegida")
        @login_requerido
        def mi_ruta():
            ...
    """
    @wraps(f)
    def decorador(*args, **kwargs):
        # Verificar si hay un user_id guardado en la sesión
        if "user_id" not in session:
            return respuesta_error("Debes iniciar sesión", 401)
        # Si está logueado, continuar con la función original
        return f(*args, **kwargs)
    return decorador
