"""
game_state.py - Funciones para gestionar el estado de partidas multijugador.
Maneja la logica del Blackjack: barajar, repartir, calcular valores,
turno del crupier, y persistencia en la tabla estado_partida.
"""

import json
import random
from database.connection import get_db, close_db


# Palos y valores de la baraja
PALOS = ['♠', '♥', '♦', '♣']
VALORES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']


def crear_baraja():
    """
    Crea una baraja de 52 cartas y la mezcla.
    Cada carta es un string como "A♠" o "10♥".
    """
    baraja = []
    for palo in PALOS:
        for valor in VALORES:
            baraja.append(valor + palo)
    random.shuffle(baraja)
    return baraja


def calcular_valor_mano(cartas):
    """
    Calcula el valor de una mano de blackjack.
    - Figuras (J, Q, K) valen 10
    - As vale 11, pero si te pasas de 21 vale 1
    - Devuelve el total optimo
    """
    total = 0
    ases = 0

    for carta in cartas:
        # Separar el valor del palo (el palo es el ultimo caracter)
        valor = carta[:-1]

        if valor in ['J', 'Q', 'K']:
            total += 10
        elif valor == 'A':
            total += 11
            ases += 1
        else:
            total += int(valor)

    # Si nos pasamos de 21, convertir ases de 11 a 1
    while total > 21 and ases > 0:
        total -= 10
        ases -= 1

    return total


def es_blackjack(cartas):
    """
    Devuelve True si la mano es un blackjack natural
    (exactamente 2 cartas que suman 21).
    """
    return len(cartas) == 2 and calcular_valor_mano(cartas) == 21


def jugar_crupier(baraja, mano_crupier):
    """
    El crupier pide cartas hasta llegar a 17 o mas.
    Devuelve la mano final del crupier y la baraja actualizada.
    """
    while calcular_valor_mano(mano_crupier) < 17:
        mano_crupier.append(baraja.pop())
    return mano_crupier, baraja


def iniciar_blackjack(sala_id, jugadores):
    """
    Inicia una partida de blackjack multijugador.
    - Crea la baraja y reparte 2 cartas a cada jugador y al crupier.
    - Guarda el estado en la base de datos.
    - jugadores es una lista de IDs de usuario.
    - Devuelve el estado creado o None si falla.
    """
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor()

        # Crear baraja y repartir
        baraja = crear_baraja()

        # Repartir 2 cartas a cada jugador
        manos = {}
        for jugador_id in jugadores:
            manos[str(jugador_id)] = [baraja.pop(), baraja.pop()]

        # Repartir 2 cartas al crupier (la segunda estara oculta)
        mano_crupier = [baraja.pop(), baraja.pop()]

        # Estado inicial: todos los jugadores estan "jugando"
        estados_jugador = {}
        for jugador_id in jugadores:
            # Comprobar si tiene blackjack natural
            if es_blackjack(manos[str(jugador_id)]):
                estados_jugador[str(jugador_id)] = "blackjack"
            else:
                estados_jugador[str(jugador_id)] = "jugando"

        # Orden de turnos y turno actual
        turno_orden = [int(j) for j in jugadores]
        turno_actual = 0

        # Buscar el primer jugador que pueda jugar (no tiene blackjack)
        while turno_actual < len(turno_orden):
            uid = str(turno_orden[turno_actual])
            if estados_jugador[uid] == "jugando":
                break
            turno_actual += 1

        # Construir el estado completo de la partida
        estado = {
            "baraja": baraja,
            "manos": manos,
            "mano_crupier": mano_crupier,
            "apuestas": {},
            "estados_jugador": estados_jugador,
            "turno_orden": turno_orden,
            "turno_actual": turno_actual
        }

        estado_json = json.dumps(estado)

        # Determinar de quien es el turno ahora
        turno_uid = None
        if turno_actual < len(turno_orden):
            turno_uid = turno_orden[turno_actual]

        # Guardar en la base de datos
        query = """
            INSERT INTO estado_partida (sala_id, juego, estado, turno_usuario_id, fase)
            VALUES (%s, 'blackjack', %s, %s, 'jugando')
            ON DUPLICATE KEY UPDATE
                estado = VALUES(estado),
                turno_usuario_id = VALUES(turno_usuario_id),
                fase = VALUES(fase)
        """
        cursor.execute(query, (sala_id, estado_json, turno_uid))
        conexion.commit()

        return estado

    except Exception as e:
        print(f"Error al iniciar blackjack: {e}")
        return None

    finally:
        if conexion:
            close_db(conexion)


def obtener_estado(sala_id):
    """
    Obtiene el estado actual de la partida de una sala.
    Devuelve un diccionario con el estado o None si no hay partida.
    """
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor(dictionary=True)

        query = """
            SELECT * FROM estado_partida
            WHERE sala_id = %s
            ORDER BY actualizado_at DESC
            LIMIT 1
        """
        cursor.execute(query, (sala_id,))
        resultado = cursor.fetchone()

        if not resultado:
            return None

        # Parsear el JSON del estado
        resultado["estado"] = json.loads(resultado["estado"])
        if resultado.get("actualizado_at"):
            resultado["actualizado_at"] = str(resultado["actualizado_at"])

        return resultado

    except Exception as e:
        print(f"Error al obtener estado: {e}")
        return None

    finally:
        if conexion:
            close_db(conexion)


def actualizar_estado(sala_id, nuevo_estado, turno_uid=None, fase="jugando"):
    """
    Guarda el estado actualizado de la partida en la base de datos.
    Devuelve True si se actualizo correctamente.
    """
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor()

        estado_json = json.dumps(nuevo_estado)

        query = """
            UPDATE estado_partida
            SET estado = %s, turno_usuario_id = %s, fase = %s
            WHERE sala_id = %s
        """
        cursor.execute(query, (estado_json, turno_uid, fase, sala_id))
        conexion.commit()

        return True

    except Exception as e:
        print(f"Error al actualizar estado: {e}")
        return False

    finally:
        if conexion:
            close_db(conexion)


def eliminar_estado(sala_id):
    """
    Borra el estado de la partida de una sala (cuando termina la partida).
    Devuelve True si se borro correctamente.
    """
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor()

        cursor.execute("DELETE FROM estado_partida WHERE sala_id = %s", (sala_id,))
        conexion.commit()

        return True

    except Exception as e:
        print(f"Error al eliminar estado: {e}")
        return False

    finally:
        if conexion:
            close_db(conexion)
