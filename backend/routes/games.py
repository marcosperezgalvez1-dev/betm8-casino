"""
games.py - Rutas de juegos.
Maneja la logica multijugador del Blackjack con polling.
Los clientes preguntan cada 2 segundos el estado de la partida.
"""

from flask import Blueprint, request, session
from utils.helpers import respuesta_ok, respuesta_error, login_requerido
from models.game_state import (
    iniciar_blackjack, obtener_estado, actualizar_estado,
    eliminar_estado, calcular_valor_mano, es_blackjack, jugar_crupier
)
from models.room import obtener_sala, actualizar_estado_sala
from database.connection import get_db, close_db

# Crear el blueprint de juegos
games_bp = Blueprint("games", __name__)


# ============================================
# POST /api/games/blackjack/<sala_id>/iniciar
# Solo el host puede iniciar la partida.
# ============================================
@games_bp.route("/blackjack/<int:sala_id>/iniciar", methods=["POST"])
@login_requerido
def iniciar_partida(sala_id):
    """Inicia una partida de blackjack en la sala."""
    user_id = session["user_id"]

    # Verificar que la sala existe
    sala = obtener_sala(sala_id)
    if not sala:
        return respuesta_error("La sala no existe", 404)

    # Solo el host puede iniciar
    if sala["host_id"] != user_id:
        return respuesta_error("Solo el host puede iniciar la partida", 403)

    # Obtener los jugadores activos de la sala
    jugadores = sala.get("jugadores", [])
    if len(jugadores) < 1:
        return respuesta_error("No hay jugadores en la sala")

    # Lista de IDs de jugadores
    ids_jugadores = [j["usuario_id"] for j in jugadores]

    # Iniciar la partida
    estado = iniciar_blackjack(sala_id, ids_jugadores)
    if not estado:
        return respuesta_error("Error al iniciar la partida")

    # Cambiar estado de la sala a 'jugando'
    actualizar_estado_sala(sala_id, "jugando")

    # Preparar respuesta (ocultar baraja y carta del crupier)
    estado_publico = preparar_estado_publico(estado)

    return respuesta_ok({"estado": estado_publico, "mensaje": "Partida iniciada"})


# ============================================
# GET /api/games/blackjack/<sala_id>/estado
# Devuelve el estado actual (polling cada 2s).
# ============================================
@games_bp.route("/blackjack/<int:sala_id>/estado", methods=["GET"])
@login_requerido
def obtener_estado_partida(sala_id):
    """Devuelve el estado actual de la partida para el polling."""
    resultado = obtener_estado(sala_id)

    if not resultado:
        return respuesta_ok({"estado": None, "fase": "esperando"})

    estado = resultado["estado"]
    fase = resultado["fase"]

    # Si la partida sigue activa, ocultar carta del crupier
    if fase == "jugando":
        estado_publico = preparar_estado_publico(estado)
    else:
        # Partida finalizada: mostrar todo
        estado_publico = {
            "manos": estado["manos"],
            "mano_crupier": estado["mano_crupier"],
            "apuestas": estado["apuestas"],
            "estados_jugador": estado["estados_jugador"],
            "turno_orden": estado["turno_orden"],
            "turno_actual": estado["turno_actual"]
        }

    return respuesta_ok({
        "estado": estado_publico,
        "fase": fase,
        "turno_usuario_id": resultado["turno_usuario_id"]
    })


# ============================================
# POST /api/games/blackjack/<sala_id>/apostar
# El jugador registra su apuesta.
# ============================================
@games_bp.route("/blackjack/<int:sala_id>/apostar", methods=["POST"])
@login_requerido
def apostar(sala_id):
    """Registra la apuesta de un jugador."""
    user_id = session["user_id"]
    datos = request.get_json()

    if not datos or "cantidad" not in datos:
        return respuesta_error("Falta la cantidad de la apuesta")

    cantidad = int(datos["cantidad"])
    if cantidad <= 0:
        return respuesta_error("La apuesta debe ser mayor a 0")

    # Obtener estado actual
    resultado = obtener_estado(sala_id)
    if not resultado:
        return respuesta_error("No hay partida activa")

    estado = resultado["estado"]

    # Verificar que el jugador esta en la partida
    uid_str = str(user_id)
    if uid_str not in estado["manos"]:
        return respuesta_error("No estas en esta partida")

    # Verificar fichas del jugador en la sala
    conexion = None
    try:
        conexion = get_db()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT fichas FROM sala_jugadores WHERE sala_id = %s AND usuario_id = %s AND activo = 1",
            (sala_id, user_id)
        )
        jugador = cursor.fetchone()
        if not jugador or jugador["fichas"] < cantidad:
            return respuesta_error("Fichas insuficientes")
    finally:
        if conexion:
            close_db(conexion)

    # Registrar la apuesta
    estado["apuestas"][uid_str] = cantidad

    # Guardar estado actualizado
    turno_uid = None
    if estado["turno_actual"] < len(estado["turno_orden"]):
        turno_uid = estado["turno_orden"][estado["turno_actual"]]
    actualizar_estado(sala_id, estado, turno_uid, "jugando")

    return respuesta_ok({"mensaje": "Apuesta registrada", "cantidad": cantidad})


# ============================================
# POST /api/games/blackjack/<sala_id>/pedir
# El jugador pide una carta (hit).
# ============================================
@games_bp.route("/blackjack/<int:sala_id>/pedir", methods=["POST"])
@login_requerido
def pedir_carta(sala_id):
    """El jugador pide una carta mas."""
    user_id = session["user_id"]

    # Obtener estado actual
    resultado = obtener_estado(sala_id)
    if not resultado or resultado["fase"] != "jugando":
        return respuesta_error("No hay partida activa")

    estado = resultado["estado"]
    uid_str = str(user_id)

    # Verificar que es el turno de este jugador
    turno_actual = estado["turno_actual"]
    if turno_actual >= len(estado["turno_orden"]):
        return respuesta_error("La ronda de jugadores ya termino")

    jugador_turno = estado["turno_orden"][turno_actual]
    if jugador_turno != user_id:
        return respuesta_error("No es tu turno")

    # Verificar que el jugador puede jugar
    if estado["estados_jugador"][uid_str] != "jugando":
        return respuesta_error("Ya no puedes pedir cartas")

    # Sacar una carta de la baraja
    if len(estado["baraja"]) == 0:
        return respuesta_error("No quedan cartas en la baraja")

    nueva_carta = estado["baraja"].pop()
    estado["manos"][uid_str].append(nueva_carta)

    # Calcular valor de la mano
    valor_mano = calcular_valor_mano(estado["manos"][uid_str])

    # Si se paso de 21, marcar como bust y pasar turno
    if valor_mano > 21:
        estado["estados_jugador"][uid_str] = "bust"
        estado = pasar_turno(sala_id, estado)
    elif valor_mano == 21:
        estado["estados_jugador"][uid_str] = "blackjack"
        estado = pasar_turno(sala_id, estado)

    # Guardar estado
    turno_uid = None
    fase = "jugando"
    if estado["turno_actual"] < len(estado["turno_orden"]):
        turno_uid = estado["turno_orden"][estado["turno_actual"]]
    else:
        # Todos han jugado, resolver partida
        estado, fase = resolver_partida(sala_id, estado)

    actualizar_estado(sala_id, estado, turno_uid, fase)

    return respuesta_ok({"mensaje": "Carta repartida", "carta": nueva_carta})


# ============================================
# POST /api/games/blackjack/<sala_id>/plantarse
# El jugador se planta (stand).
# ============================================
@games_bp.route("/blackjack/<int:sala_id>/plantarse", methods=["POST"])
@login_requerido
def plantarse(sala_id):
    """El jugador se planta y pasa al siguiente turno."""
    user_id = session["user_id"]

    # Obtener estado actual
    resultado = obtener_estado(sala_id)
    if not resultado or resultado["fase"] != "jugando":
        return respuesta_error("No hay partida activa")

    estado = resultado["estado"]
    uid_str = str(user_id)

    # Verificar que es el turno de este jugador
    turno_actual = estado["turno_actual"]
    if turno_actual >= len(estado["turno_orden"]):
        return respuesta_error("La ronda de jugadores ya termino")

    jugador_turno = estado["turno_orden"][turno_actual]
    if jugador_turno != user_id:
        return respuesta_error("No es tu turno")

    # Marcar como plantado
    estado["estados_jugador"][uid_str] = "plantado"

    # Pasar al siguiente turno
    estado = pasar_turno(sala_id, estado)

    # Guardar estado
    turno_uid = None
    fase = "jugando"
    if estado["turno_actual"] < len(estado["turno_orden"]):
        turno_uid = estado["turno_orden"][estado["turno_actual"]]
    else:
        # Todos han jugado, resolver partida
        estado, fase = resolver_partida(sala_id, estado)

    actualizar_estado(sala_id, estado, turno_uid, fase)

    return respuesta_ok({"mensaje": "Te has plantado"})


# ============================================
# GET /api/games/blackjack/<sala_id>/resultado
# Devuelve los resultados finales de la partida.
# ============================================
@games_bp.route("/blackjack/<int:sala_id>/resultado", methods=["GET"])
@login_requerido
def obtener_resultado(sala_id):
    """Devuelve ganadores, perdedores y fichas ganadas/perdidas."""
    resultado = obtener_estado(sala_id)
    if not resultado:
        return respuesta_error("No hay partida")

    if resultado["fase"] != "finalizada":
        return respuesta_error("La partida aun no ha terminado")

    estado = resultado["estado"]
    resultados = estado.get("resultados", {})

    return respuesta_ok({"resultados": resultados, "mano_crupier": estado["mano_crupier"]})


# ============================================
# Funciones auxiliares
# ============================================

def preparar_estado_publico(estado):
    """
    Prepara el estado para enviar al cliente.
    Oculta la baraja y la segunda carta del crupier.
    """
    mano_crupier_visible = [estado["mano_crupier"][0], "?"]

    return {
        "manos": estado["manos"],
        "mano_crupier": mano_crupier_visible,
        "apuestas": estado["apuestas"],
        "estados_jugador": estado["estados_jugador"],
        "turno_orden": estado["turno_orden"],
        "turno_actual": estado["turno_actual"]
    }


def pasar_turno(sala_id, estado):
    """
    Avanza al siguiente jugador que pueda jugar.
    Salta a los que ya estan bust, plantados o con blackjack.
    """
    estado["turno_actual"] += 1

    # Buscar el siguiente jugador que este "jugando"
    while estado["turno_actual"] < len(estado["turno_orden"]):
        uid = str(estado["turno_orden"][estado["turno_actual"]])
        if estado["estados_jugador"][uid] == "jugando":
            break
        estado["turno_actual"] += 1

    return estado


def resolver_partida(sala_id, estado):
    """
    Todos los jugadores han terminado. El crupier juega y se calculan
    los ganadores. Actualiza fichas en sala_jugadores y transacciones.
    Devuelve el estado con resultados y la fase 'finalizada'.
    """
    # El crupier juega
    mano_crupier, baraja = jugar_crupier(estado["baraja"], estado["mano_crupier"])
    estado["mano_crupier"] = mano_crupier
    estado["baraja"] = baraja

    valor_crupier = calcular_valor_mano(mano_crupier)
    crupier_bust = valor_crupier > 21

    # Calcular resultado de cada jugador
    resultados = {}
    conexion = None

    try:
        conexion = get_db()
        cursor = conexion.cursor()

        for uid_str, mano in estado["manos"].items():
            valor_jugador = calcular_valor_mano(mano)
            apuesta = estado["apuestas"].get(uid_str, 0)
            estado_jugador = estado["estados_jugador"][uid_str]
            ganancia = 0
            resultado_texto = ""

            if estado_jugador == "bust":
                # El jugador se paso: pierde su apuesta
                ganancia = -apuesta
                resultado_texto = "bust"

            elif estado_jugador == "blackjack" and not es_blackjack(mano_crupier):
                # Blackjack natural del jugador (y crupier no tiene): paga 3:2
                ganancia = int(apuesta * 1.5)
                resultado_texto = "blackjack"

            elif es_blackjack(mano_crupier) and estado_jugador == "blackjack":
                # Ambos tienen blackjack: empate
                ganancia = 0
                resultado_texto = "empate"

            elif es_blackjack(mano_crupier):
                # Solo el crupier tiene blackjack: jugador pierde
                ganancia = -apuesta
                resultado_texto = "pierde"

            elif crupier_bust:
                # Crupier se paso: jugador gana
                ganancia = apuesta
                resultado_texto = "gana"

            elif valor_jugador > valor_crupier:
                # Jugador tiene mas que crupier
                ganancia = apuesta
                resultado_texto = "gana"

            elif valor_jugador == valor_crupier:
                # Empate: se devuelve la apuesta
                ganancia = 0
                resultado_texto = "empate"

            else:
                # Crupier tiene mas: jugador pierde
                ganancia = -apuesta
                resultado_texto = "pierde"

            resultados[uid_str] = {
                "resultado": resultado_texto,
                "valor_mano": valor_jugador,
                "ganancia": ganancia,
                "apuesta": apuesta
            }

            # Actualizar fichas en sala_jugadores
            if ganancia != 0:
                cursor.execute(
                    "UPDATE sala_jugadores SET fichas = fichas + %s WHERE sala_id = %s AND usuario_id = %s",
                    (ganancia, sala_id, int(uid_str))
                )

                # Registrar transaccion
                tipo = "ganancia" if ganancia > 0 else "apuesta"
                descripcion = f"Blackjack: {resultado_texto} (apuesta: {apuesta})"
                cursor.execute(
                    """INSERT INTO transacciones (usuario_id, sala_id, cantidad, tipo, descripcion)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (int(uid_str), sala_id, ganancia, tipo, descripcion)
                )

        conexion.commit()

    except Exception as e:
        print(f"Error al resolver partida: {e}")

    finally:
        if conexion:
            close_db(conexion)

    # Guardar resultados en el estado
    estado["resultados"] = resultados

    return estado, "finalizada"
