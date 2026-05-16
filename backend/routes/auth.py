"""
auth.py - Rutas de autenticación.
Maneja el registro, login y logout de usuarios.
Todas las rutas devuelven JSON.
"""

from flask import Blueprint, request, session
from werkzeug.security import check_password_hash
from models.user import crear_usuario, buscar_por_username_o_email, buscar_por_id
from utils.helpers import respuesta_ok, respuesta_error, login_requerido

# Crear el blueprint de autenticación
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Registrar un nuevo usuario.
    Recibe JSON: { username, email, password }
    Devuelve: { ok, user }
    """
    # Obtener los datos del cuerpo de la petición
    datos = request.get_json()

    # Verificar que nos enviaron todos los campos
    if not datos:
        return respuesta_error("No se recibieron datos")

    username = datos.get("username", "").strip()
    email = datos.get("email", "").strip()
    password = datos.get("password", "")

    # --- Validaciones básicas ---
    if not username or not email or not password:
        return respuesta_error("Todos los campos son obligatorios")

    if len(username) < 3:
        return respuesta_error("El nombre de usuario debe tener al menos 3 caracteres")

    if len(password) < 6:
        return respuesta_error("La contraseña debe tener al menos 6 caracteres")

    if "@" not in email:
        return respuesta_error("El email no es válido")

    # --- Verificar que no exista ya ---
    existente = buscar_por_username_o_email(username)
    if existente:
        return respuesta_error("El nombre de usuario ya está en uso")

    existente = buscar_por_username_o_email(email)
    if existente:
        return respuesta_error("El email ya está registrado")

    # --- Crear el usuario ---
    usuario = crear_usuario(username, email, password)
    if not usuario:
        return respuesta_error("Error al crear el usuario", 500)

    # Guardar el ID del usuario en la sesión (queda logueado automáticamente)
    session["user_id"] = usuario["id"]

    return respuesta_ok({"user": usuario})


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Iniciar sesión.
    Recibe JSON: { username_or_email, password }
    Devuelve: { ok, user }
    """
    datos = request.get_json()

    if not datos:
        return respuesta_error("No se recibieron datos")

    username_or_email = datos.get("username_or_email", "").strip()
    password = datos.get("password", "")

    if not username_or_email or not password:
        return respuesta_error("Todos los campos son obligatorios")

    # Buscar al usuario en la base de datos
    usuario = buscar_por_username_o_email(username_or_email)
    if not usuario:
        return respuesta_error("Usuario o contraseña incorrectos")

    # Verificar la contraseña comparando con el hash guardado
    if not check_password_hash(usuario["password_hash"], password):
        return respuesta_error("Usuario o contraseña incorrectos")

    # Guardar el ID en la sesión
    session["user_id"] = usuario["id"]

    # Preparar los datos del usuario para la respuesta (sin password_hash)
    datos_usuario = {
        "id": usuario["id"],
        "username": usuario["username"],
        "email": usuario["email"],
        "coins": usuario["coins"],
        "xp": usuario["xp"],
        "level": usuario["level"],
        "avatar": usuario["avatar"],
        "games_played": usuario["games_played"],
        "total_won": usuario["total_won"]
    }

    return respuesta_ok({"user": datos_usuario})


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    Cerrar sesión.
    Elimina los datos de la sesión del usuario.
    """
    # Limpiar toda la sesión
    session.clear()
    return respuesta_ok({"message": "Sesión cerrada correctamente"})


@auth_bp.route("/me", methods=["GET"])
@login_requerido
def me():
    """
    Obtener los datos del usuario actual.
    Solo funciona si el usuario está logueado (gracias al decorador login_requerido).
    Devuelve: { ok, user }
    """
    # Obtener el ID del usuario desde la sesión
    user_id = session["user_id"]

    # Buscar los datos actualizados del usuario
    usuario = buscar_por_id(user_id)
    if not usuario:
        return respuesta_error("Usuario no encontrado", 404)

    return respuesta_ok({"user": usuario})
