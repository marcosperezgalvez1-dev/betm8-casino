"""
room.py - Funciones relacionadas con las salas.
Consultas a la base de datos para crear, buscar, unirse y gestionar salas.
"""

import random
import string
from werkzeug.security import generate_password_hash, check_password_hash
from database.connection import get_db, close_db


def generar_codigo_invitacion():
    """
    Genera un código de invitación aleatorio de 6 caracteres.
    Usa letras mayúsculas y números para que sea fácil de compartir.
    Ejemplo: "A3K9B2"
    """
    caracteres = string.ascii_uppercase + string.digits
    return "".join(random.choice(caracteres) for _ in range(6))


def crear_sala(nombre, juego, host_id, tipo="publica", password=None,
               max_jugadores=4, fichas_inicio=100, es_torneo=False):
    """
    Crea una nueva sala en la base de datos.
    - Genera un código de invitación único.
    - Si la sala es privada, hashea la contraseña.
    - Añade al host (creador) como primer jugador de la sala.
    - Devuelve un diccionario con los datos de la sala creada.
    """
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor()

        # Generar código de invitación único
        codigo_inv = generar_codigo_invitacion()

        # Si la sala es privada y tiene contraseña, hashearla
        password_hash = None
        if tipo == "privada" and password:
            password_hash = generate_password_hash(password)

        # Insertar la sala en la base de datos
        query = """
            INSERT INTO salas (nombre, juego, host_id, tipo, password,
                               max_jugadores, fichas_inicio, estado,
                               codigo_inv, es_torneo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'esperando', %s, %s)
        """
        cursor.execute(query, (nombre, juego, host_id, tipo, password_hash,
                               max_jugadores, fichas_inicio, codigo_inv, es_torneo))

        sala_id = cursor.lastrowid

        # Añadir al host como primer jugador de la sala
        query_jugador = """
            INSERT INTO sala_jugadores (sala_id, usuario_id, fichas)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query_jugador, (sala_id, host_id, fichas_inicio))

        conexion.commit()

        # Devolver los datos de la sala creada
        sala = {
            "id": sala_id,
            "nombre": nombre,
            "juego": juego,
            "host_id": host_id,
            "tipo": tipo,
            "max_jugadores": max_jugadores,
            "fichas_inicio": fichas_inicio,
            "estado": "esperando",
            "codigo_inv": codigo_inv,
            "es_torneo": es_torneo,
            "jugadores_actuales": 1
        }
        return sala

    except Exception as e:
        print(f"Error al crear sala: {e}")
        return None

    finally:
        if conexion:
            close_db(conexion)


def listar_salas(filtro_juego=None, filtro_tipo=None, filtro_estado=None, busqueda=None):
    """
    Lista todas las salas con el número de jugadores actuales.
    Se pueden aplicar filtros opcionales por juego, tipo, estado o búsqueda por nombre.
    Devuelve una lista de diccionarios.
    """
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor(dictionary=True)

        # Query base: salas con conteo de jugadores activos y nombre del host
        query = """
            SELECT s.*,
                   u.username AS host_username,
                   COUNT(sp.id) AS jugadores_actuales
            FROM salas s
            LEFT JOIN sala_jugadores sp ON s.id = sp.sala_id AND sp.activo = 1
            LEFT JOIN usuarios u ON s.host_id = u.id
        """

        # Construir los filtros dinámicamente
        condiciones = []
        parametros = []

        if filtro_juego:
            condiciones.append("s.juego = %s")
            parametros.append(filtro_juego)

        if filtro_tipo:
            condiciones.append("s.tipo = %s")
            parametros.append(filtro_tipo)

        if filtro_estado:
            condiciones.append("s.estado = %s")
            parametros.append(filtro_estado)

        if busqueda:
            condiciones.append("s.nombre LIKE %s")
            parametros.append(f"%{busqueda}%")

        # Añadir las condiciones al query si hay alguna
        if condiciones:
            query += " WHERE " + " AND ".join(condiciones)

        query += " GROUP BY s.id ORDER BY s.created_at DESC"

        cursor.execute(query, parametros)
        salas = cursor.fetchall()

        # Convertir fechas a string para que sean serializables a JSON
        for sala in salas:
            if sala.get("created_at"):
                sala["created_at"] = str(sala["created_at"])
            # No enviar la contraseña hasheada al frontend
            sala.pop("password", None)

        return salas

    except Exception as e:
        print(f"Error al listar salas: {e}")
        return []

    finally:
        if conexion:
            close_db(conexion)


def obtener_sala(sala_id):
    """
    Obtiene los datos completos de una sala con la lista de jugadores.
    Devuelve un diccionario con la info de la sala + array de jugadores.
    """
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor(dictionary=True)

        # Obtener datos de la sala con el nombre del host
        query_sala = """
            SELECT s.*, u.username AS host_username
            FROM salas s
            LEFT JOIN usuarios u ON s.host_id = u.id
            WHERE s.id = %s
        """
        cursor.execute(query_sala, (sala_id,))
        sala = cursor.fetchone()

        if not sala:
            return None

        # Convertir fecha a string
        if sala.get("created_at"):
            sala["created_at"] = str(sala["created_at"])
        # No enviar la contraseña hasheada
        sala.pop("password", None)

        # Obtener la lista de jugadores activos en la sala
        query_jugadores = """
            SELECT sp.usuario_id, sp.fichas, sp.activo,
                   u.username, u.avatar, u.level
            FROM sala_jugadores sp
            JOIN usuarios u ON sp.usuario_id = u.id
            WHERE sp.sala_id = %s AND sp.activo = 1
        """
        cursor.execute(query_jugadores, (sala_id,))
        jugadores = cursor.fetchall()

        sala["jugadores"] = jugadores
        sala["jugadores_actuales"] = len(jugadores)

        return sala

    except Exception as e:
        print(f"Error al obtener sala: {e}")
        return None

    finally:
        if conexion:
            close_db(conexion)


def obtener_sala_por_codigo(codigo):
    """
    Busca una sala por su código de invitación.
    Devuelve los datos de la sala o None si no existe.
    """
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor(dictionary=True)

        query = """
            SELECT s.*, u.username AS host_username,
                   COUNT(sp.id) AS jugadores_actuales
            FROM salas s
            LEFT JOIN sala_jugadores sp ON s.id = sp.sala_id AND sp.activo = 1
            LEFT JOIN usuarios u ON s.host_id = u.id
            WHERE s.codigo_inv = %s
            GROUP BY s.id
        """
        cursor.execute(query, (codigo,))
        sala = cursor.fetchone()

        if sala:
            if sala.get("created_at"):
                sala["created_at"] = str(sala["created_at"])
            sala.pop("password", None)

        return sala

    except Exception as e:
        print(f"Error al buscar sala por código: {e}")
        return None

    finally:
        if conexion:
            close_db(conexion)


def unirse_sala(sala_id, usuario_id, password=None):
    """
    Añade un jugador a una sala.
    - Verifica que la sala no esté llena.
    - Si la sala es privada, verifica la contraseña.
    - Si el jugador ya estuvo antes, lo reactiva.
    Devuelve (True, mensaje) si todo fue bien, o (False, error) si falló.
    """
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor(dictionary=True)

        # Obtener datos de la sala
        cursor.execute("SELECT * FROM salas WHERE id = %s", (sala_id,))
        sala = cursor.fetchone()

        if not sala:
            return False, "La sala no existe"

        if sala["estado"] == "finalizada":
            return False, "La sala ya ha finalizado"

        # Verificar contraseña si es privada
        if sala["tipo"] == "privada" and sala["password"]:
            if not password:
                return False, "Esta sala requiere contraseña"
            if not check_password_hash(sala["password"], password):
                return False, "Contraseña incorrecta"

        # Contar jugadores activos
        cursor.execute(
            "SELECT COUNT(*) AS total FROM sala_jugadores WHERE sala_id = %s AND activo = 1",
            (sala_id,)
        )
        resultado = cursor.fetchone()
        jugadores_actuales = resultado["total"]

        if jugadores_actuales >= sala["max_jugadores"]:
            return False, "La sala está llena"

        # Verificar si el jugador ya estuvo en la sala antes
        cursor.execute(
            "SELECT * FROM sala_jugadores WHERE sala_id = %s AND usuario_id = %s",
            (sala_id, usuario_id)
        )
        jugador_existente = cursor.fetchone()

        if jugador_existente:
            if jugador_existente["activo"]:
                return False, "Ya estás en esta sala"
            # Reactivar al jugador que había salido antes
            cursor.execute(
                "UPDATE sala_jugadores SET activo = 1, fichas = %s WHERE sala_id = %s AND usuario_id = %s",
                (sala["fichas_inicio"], sala_id, usuario_id)
            )
        else:
            # Insertar nuevo jugador
            cursor.execute(
                "INSERT INTO sala_jugadores (sala_id, usuario_id, fichas) VALUES (%s, %s, %s)",
                (sala_id, usuario_id, sala["fichas_inicio"])
            )

        conexion.commit()
        return True, "Te has unido a la sala"

    except Exception as e:
        print(f"Error al unirse a sala: {e}")
        return False, "Error al unirse a la sala"

    finally:
        if conexion:
            close_db(conexion)


def salir_sala(sala_id, usuario_id):
    """
    Marca al jugador como inactivo en la sala (no lo borra, por si quiere volver).
    Devuelve True si se actualizó correctamente.
    """
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor()

        cursor.execute(
            "UPDATE sala_jugadores SET activo = 0 WHERE sala_id = %s AND usuario_id = %s",
            (sala_id, usuario_id)
        )
        conexion.commit()
        return True

    except Exception as e:
        print(f"Error al salir de sala: {e}")
        return False

    finally:
        if conexion:
            close_db(conexion)


def actualizar_estado_sala(sala_id, estado):
    """
    Cambia el estado de una sala.
    Estados posibles: 'esperando', 'jugando', 'finalizada'.
    Devuelve True si se actualizó correctamente.
    """
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor()

        cursor.execute(
            "UPDATE salas SET estado = %s WHERE id = %s",
            (estado, sala_id)
        )
        conexion.commit()
        return True

    except Exception as e:
        print(f"Error al actualizar estado de sala: {e}")
        return False

    finally:
        if conexion:
            close_db(conexion)


def expulsar_jugador(sala_id, usuario_id):
    """
    Expulsa a un jugador de la sala marcándolo como inactivo.
    Es lo mismo que salir_sala pero lo ejecuta el host.
    """
    return salir_sala(sala_id, usuario_id)


def dar_fichas(sala_id, de_usuario_id, a_usuario_id, cantidad, motivo="reparto"):
    """
    Transfiere fichas de un jugador a otro dentro de una sala.
    - Resta fichas al que da.
    - Suma fichas al que recibe.
    - Registra la transacción en la tabla transacciones.
    Devuelve (True, mensaje) o (False, error).
    """
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor(dictionary=True)

        # Verificar que el que da tiene suficientes fichas
        cursor.execute(
            "SELECT fichas FROM sala_jugadores WHERE sala_id = %s AND usuario_id = %s AND activo = 1",
            (sala_id, de_usuario_id)
        )
        resultado = cursor.fetchone()

        if not resultado:
            return False, "El jugador que da fichas no está en la sala"

        if resultado["fichas"] < cantidad:
            return False, "No tienes suficientes fichas"

        # Verificar que el receptor está en la sala
        cursor.execute(
            "SELECT fichas FROM sala_jugadores WHERE sala_id = %s AND usuario_id = %s AND activo = 1",
            (sala_id, a_usuario_id)
        )
        receptor = cursor.fetchone()

        if not receptor:
            return False, "El jugador que recibe no está en la sala"

        # Restar fichas al que da
        cursor.execute(
            "UPDATE sala_jugadores SET fichas = fichas - %s WHERE sala_id = %s AND usuario_id = %s",
            (cantidad, sala_id, de_usuario_id)
        )

        # Sumar fichas al que recibe
        cursor.execute(
            "UPDATE sala_jugadores SET fichas = fichas + %s WHERE sala_id = %s AND usuario_id = %s",
            (cantidad, sala_id, a_usuario_id)
        )

        # Registrar la transacción
        cursor.execute(
            """INSERT INTO transacciones (usuario_id, sala_id, cantidad, tipo, descripcion)
               VALUES (%s, %s, %s, 'ganancia', %s)""",
            (a_usuario_id, sala_id, cantidad, motivo)
        )

        conexion.commit()
        return True, f"Se transfirieron {cantidad} fichas"

    except Exception as e:
        print(f"Error al dar fichas: {e}")
        return False, "Error al transferir fichas"

    finally:
        if conexion:
            close_db(conexion)
