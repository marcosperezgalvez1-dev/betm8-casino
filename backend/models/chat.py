"""
chat.py - Funciones relacionadas con el chat de las salas.
Consultas a la base de datos para enviar y obtener mensajes.
"""

from database.connection import get_db, close_db


def enviar_mensaje(sala_id, usuario_id, mensaje):
    """
    Guarda un mensaje de chat en la base de datos.
    Devuelve el diccionario del mensaje creado o None si falla.
    """
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor(dictionary=True)

        # Insertar el mensaje
        cursor.execute(
            "INSERT INTO mensajes_chat (sala_id, usuario_id, mensaje) VALUES (%s, %s, %s)",
            (sala_id, usuario_id, mensaje)
        )
        conexion.commit()

        mensaje_id = cursor.lastrowid

        # Obtener el mensaje con el username del autor
        cursor.execute(
            """SELECT mc.id, mc.sala_id, mc.usuario_id, mc.mensaje, mc.enviado_at,
                      u.username, u.avatar
               FROM mensajes_chat mc
               JOIN usuarios u ON mc.usuario_id = u.id
               WHERE mc.id = %s""",
            (mensaje_id,)
        )
        resultado = cursor.fetchone()

        if resultado and resultado.get("enviado_at"):
            resultado["enviado_at"] = str(resultado["enviado_at"])

        return resultado

    except Exception as e:
        print(f"Error al enviar mensaje: {e}")
        return None

    finally:
        if conexion:
            close_db(conexion)


def obtener_mensajes(sala_id, limite=50):
    """
    Obtiene los últimos mensajes del chat de una sala.
    Incluye el username y avatar del autor de cada mensaje.
    Los mensajes vienen ordenados del más antiguo al más reciente.
    """
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor(dictionary=True)

        # Obtener los últimos mensajes con datos del autor
        # Usamos un subquery para obtener los últimos N y luego los ordenamos cronológicamente
        query = """
            SELECT mc.id, mc.sala_id, mc.usuario_id, mc.mensaje, mc.enviado_at,
                   u.username, u.avatar
            FROM mensajes_chat mc
            JOIN usuarios u ON mc.usuario_id = u.id
            WHERE mc.sala_id = %s
            ORDER BY mc.enviado_at DESC
            LIMIT %s
        """
        cursor.execute(query, (sala_id, limite))
        mensajes = cursor.fetchall()

        # Convertir fechas a string
        for msg in mensajes:
            if msg.get("enviado_at"):
                msg["enviado_at"] = str(msg["enviado_at"])

        # Invertir el orden para que los más antiguos estén primero
        mensajes.reverse()

        return mensajes

    except Exception as e:
        print(f"Error al obtener mensajes: {e}")
        return []

    finally:
        if conexion:
            close_db(conexion)
