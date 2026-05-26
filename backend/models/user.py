"""
user.py - Funciones relacionadas con los usuarios.
Consultas a la base de datos para crear, buscar y actualizar usuarios.
"""

from werkzeug.security import generate_password_hash
from database.connection import get_db, close_db

# Fichas que recibe cada usuario nuevo al registrarse
FICHAS_INICIALES = 5000


def crear_usuario(username, email, password):
    """
    Crea un nuevo usuario en la base de datos.
    - Hashea la contraseña antes de guardarla (nunca se guarda en texto plano).
    - Le asigna las fichas iniciales (5000).
    - Devuelve un diccionario con los datos del usuario creado, o None si falla.
    """
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor()

        # Hashear la contraseña para guardarla de forma segura
        password_hash = generate_password_hash(password)

        # Insertar el nuevo usuario en la tabla
        query = """
            INSERT INTO usuarios (username, email, password_hash, coins)
            VALUES (%s, %s, %s, %s)
        """
        # RETURNING id devuelve el ID del usuario recién creado (PostgreSQL)
        query += " RETURNING id"
        cursor.execute(query, (username, email, password_hash, FICHAS_INICIALES))
        conexion.commit()

        # Obtener el ID del usuario recién creado
        user_id = cursor.fetchone()["id"]

        # Devolver los datos del usuario (sin la contraseña)
        usuario = {
            "id": user_id,
            "username": username,
            "email": email,
            "coins": FICHAS_INICIALES,
            "xp": 0,
            "level": 1,
            "avatar": "default",
            "games_played": 0,
            "total_won": 0
        }
        return usuario

    except Exception as e:
        print(f"Error al crear usuario: {e}")
        return None

    finally:
        # Siempre cerrar la conexión, pase lo que pase
        if conexion:
            close_db(conexion)


def buscar_por_username_o_email(valor):
    """
    Busca un usuario por su username O su email.
    Útil para el login, donde el usuario puede escribir cualquiera de los dos.
    Devuelve un diccionario con TODOS los datos (incluido password_hash) o None.
    """
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor()

        query = """
            SELECT * FROM usuarios
            WHERE username = %s OR email = %s
        """
        cursor.execute(query, (valor, valor))
        usuario = cursor.fetchone()

        return usuario

    except Exception as e:
        print(f"Error al buscar usuario: {e}")
        return None

    finally:
        if conexion:
            close_db(conexion)


def buscar_por_id(user_id):
    """
    Busca un usuario por su ID.
    Devuelve un diccionario SIN el password_hash (para no exponerlo).
    Se usa para obtener los datos del usuario logueado.
    """
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor()

        query = """
            SELECT id, username, email, coins, xp, level, avatar,
                   games_played, total_won, created_at
            FROM usuarios
            WHERE id = %s
        """
        cursor.execute(query, (user_id,))
        usuario = cursor.fetchone()

        # Convertir created_at a string para que sea serializable a JSON
        if usuario and usuario.get("created_at"):
            usuario["created_at"] = str(usuario["created_at"])

        return usuario

    except Exception as e:
        print(f"Error al buscar usuario por ID: {e}")
        return None

    finally:
        if conexion:
            close_db(conexion)


def actualizar_coins(user_id, cantidad):
    """
    Suma o resta fichas al usuario.
    - cantidad positiva = sumar fichas (ganancia, bonus).
    - cantidad negativa = restar fichas (apuesta).
    Devuelve True si se actualizó correctamente, False si falló.
    """
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor()

        query = """
            UPDATE usuarios
            SET coins = coins + %s
            WHERE id = %s
        """
        cursor.execute(query, (cantidad, user_id))
        conexion.commit()

        return True

    except Exception as e:
        print(f"Error al actualizar fichas: {e}")
        return False

    finally:
        if conexion:
            close_db(conexion)
