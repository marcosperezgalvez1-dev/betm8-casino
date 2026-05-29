"""
rooms.py - Rutas de salas.
Maneja la creación, listado, unión, gestión de salas y chat.
Todas las rutas devuelven JSON.
"""

from flask import Blueprint, request, session
from models.room import (
    crear_sala, listar_salas, obtener_sala, obtener_sala_por_codigo,
    unirse_sala, salir_sala, actualizar_estado_sala, expulsar_jugador, dar_fichas
)
from models.chat import enviar_mensaje, obtener_mensajes
from utils.helpers import respuesta_ok, respuesta_error, login_requerido

# Crear el blueprint de salas
rooms_bp = Blueprint("rooms", __name__)


# ============================================
# CRUD de salas
# ============================================

@rooms_bp.route("/", methods=["GET"])
def listar():
    """
    Lista todas las salas con filtros opcionales.
    Query params: game, type, status, search
    Ejemplo: /api/rooms/?game=blackjack&type=publica
    """
    # Leer los filtros de los parámetros de la URL
    filtro_juego = request.args.get("game")
    filtro_tipo = request.args.get("type")
    filtro_estado = request.args.get("status")
    busqueda = request.args.get("search")

    salas = listar_salas(filtro_juego, filtro_tipo, filtro_estado, busqueda)
    return respuesta_ok({"rooms": salas})


@rooms_bp.route("/", methods=["POST"])
@login_requerido
def crear():
    """
    Crea una nueva sala.
    Requiere estar logueado.
    Recibe JSON: { nombre, juego, tipo, password, max_jugadores, fichas_inicio, es_torneo }
    """
    datos = request.get_json()

    if not datos:
        return respuesta_error("No se recibieron datos")

    nombre = datos.get("nombre", "").strip()
    juego = datos.get("juego", "").strip()

    # Validaciones básicas
    if not nombre:
        return respuesta_error("El nombre de la sala es obligatorio")

    if not juego:
        return respuesta_error("Debes seleccionar un juego")

    # Juegos válidos
    juegos_validos = ["blackjack", "ruleta", "poker", "slots", "baccarat", "dados"]
    if juego not in juegos_validos:
        return respuesta_error(f"Juego no válido. Opciones: {', '.join(juegos_validos)}")

    # Parámetros opcionales con valores por defecto
    tipo = datos.get("tipo", "publica")
    password = datos.get("password")
    max_jugadores = datos.get("max_jugadores", 4)
    fichas_inicio = datos.get("fichas_inicio", 100)
    es_torneo = datos.get("es_torneo", False)

    # Validar max_jugadores
    if max_jugadores < 2 or max_jugadores > 10:
        return respuesta_error("El número de jugadores debe ser entre 2 y 10")

    # Validar fichas_inicio
    if fichas_inicio < 10 or fichas_inicio > 10000:
        return respuesta_error("Las fichas iniciales deben ser entre 10 y 10000")

    # Si es tipo 'password', necesita contraseña
    if tipo == "password" and not password:
        return respuesta_error("Las salas con contraseña necesitan una clave")

    # Obtener el ID del usuario logueado (será el host)
    host_id = session["user_id"]

    # Crear la sala
    sala = crear_sala(nombre, juego, host_id, tipo, password,
                      max_jugadores, fichas_inicio, es_torneo)

    if not sala:
        return respuesta_error("Error al crear la sala", 500)

    return respuesta_ok({"room": sala})


@rooms_bp.route("/<int:sala_id>", methods=["GET"])
def detalle(sala_id):
    """
    Obtiene los datos completos de una sala con su lista de jugadores.
    """
    sala = obtener_sala(sala_id)

    if not sala:
        return respuesta_error("Sala no encontrada", 404)

    return respuesta_ok({"room": sala})


# ============================================
# Unirse y salir de salas
# ============================================

@rooms_bp.route("/<int:sala_id>/join", methods=["POST"])
@login_requerido
def unirse(sala_id):
    """
    Unirse a una sala.
    Si la sala es privada, recibe JSON: { password }
    """
    usuario_id = session["user_id"]
    datos = request.get_json() or {}
    password = datos.get("password")

    exito, mensaje = unirse_sala(sala_id, usuario_id, password)

    if not exito:
        return respuesta_error(mensaje)

    return respuesta_ok({"message": mensaje})


@rooms_bp.route("/<int:sala_id>/leave", methods=["POST"])
@login_requerido
def salir(sala_id):
    """
    Salir de una sala.
    El jugador queda marcado como inactivo (puede volver a unirse después).
    """
    usuario_id = session["user_id"]

    if salir_sala(sala_id, usuario_id):
        return respuesta_ok({"message": "Has salido de la sala"})
    else:
        return respuesta_error("Error al salir de la sala", 500)


# ============================================
# Gestión del host (solo el creador de la sala)
# ============================================

@rooms_bp.route("/<int:sala_id>/start", methods=["POST"])
@login_requerido
def iniciar_partida(sala_id):
    """
    Inicia la partida en la sala.
    Solo el host puede hacerlo. Cambia el estado a 'jugando'.
    """
    usuario_id = session["user_id"]

    # Verificar que el usuario es el host
    sala = obtener_sala(sala_id)
    if not sala:
        return respuesta_error("Sala no encontrada", 404)

    if sala["host_id"] != usuario_id:
        return respuesta_error("Solo el host puede iniciar la partida", 403)

    if sala["estado"] != "esperando":
        return respuesta_error("La sala no está en estado de espera")

    if actualizar_estado_sala(sala_id, "jugando"):
        return respuesta_ok({"message": "Partida iniciada"})
    else:
        return respuesta_error("Error al iniciar la partida", 500)


@rooms_bp.route("/<int:sala_id>/pause", methods=["POST"])
@login_requerido
def pausar_partida(sala_id):
    """
    Pausa la partida. Solo el host.
    Cambia el estado de 'jugando' a 'esperando'.
    """
    usuario_id = session["user_id"]

    sala = obtener_sala(sala_id)
    if not sala:
        return respuesta_error("Sala no encontrada", 404)

    if sala["host_id"] != usuario_id:
        return respuesta_error("Solo el host puede pausar la partida", 403)

    if sala["estado"] != "jugando":
        return respuesta_error("La sala no está en juego")

    if actualizar_estado_sala(sala_id, "esperando"):
        return respuesta_ok({"message": "Partida pausada"})
    else:
        return respuesta_error("Error al pausar la partida", 500)


@rooms_bp.route("/<int:sala_id>/end", methods=["POST"])
@login_requerido
def finalizar_partida(sala_id):
    """
    Finaliza la partida. Solo el host.
    Cambia el estado a 'finalizada'.
    """
    usuario_id = session["user_id"]

    sala = obtener_sala(sala_id)
    if not sala:
        return respuesta_error("Sala no encontrada", 404)

    if sala["host_id"] != usuario_id:
        return respuesta_error("Solo el host puede finalizar la partida", 403)

    if actualizar_estado_sala(sala_id, "finalizada"):
        return respuesta_ok({"message": "Partida finalizada"})
    else:
        return respuesta_error("Error al finalizar la partida", 500)


@rooms_bp.route("/<int:sala_id>/kick", methods=["POST"])
@login_requerido
def expulsar(sala_id):
    """
    Expulsa a un jugador de la sala. Solo el host.
    Recibe JSON: { usuario_id }
    """
    usuario_id = session["user_id"]
    datos = request.get_json()

    if not datos or not datos.get("usuario_id"):
        return respuesta_error("Debes indicar el usuario a expulsar")

    # Verificar que el usuario es el host
    sala = obtener_sala(sala_id)
    if not sala:
        return respuesta_error("Sala no encontrada", 404)

    if sala["host_id"] != usuario_id:
        return respuesta_error("Solo el host puede expulsar jugadores", 403)

    jugador_a_expulsar = datos["usuario_id"]

    # No puede expulsarse a sí mismo
    if jugador_a_expulsar == usuario_id:
        return respuesta_error("No puedes expulsarte a ti mismo")

    if expulsar_jugador(sala_id, jugador_a_expulsar):
        return respuesta_ok({"message": "Jugador expulsado"})
    else:
        return respuesta_error("Error al expulsar al jugador", 500)


@rooms_bp.route("/<int:sala_id>/give-coins", methods=["POST"])
@login_requerido
def repartir_fichas(sala_id):
    """
    Reparte fichas de un jugador a otro. Solo el host.
    Recibe JSON: { a_usuario_id, cantidad, motivo }
    """
    usuario_id = session["user_id"]
    datos = request.get_json()

    if not datos:
        return respuesta_error("No se recibieron datos")

    # Verificar que el usuario es el host
    sala = obtener_sala(sala_id)
    if not sala:
        return respuesta_error("Sala no encontrada", 404)

    if sala["host_id"] != usuario_id:
        return respuesta_error("Solo el host puede repartir fichas", 403)

    a_usuario_id = datos.get("a_usuario_id")
    cantidad = datos.get("cantidad", 0)
    motivo = datos.get("motivo", "reparto del host")

    if not a_usuario_id:
        return respuesta_error("Debes indicar a quién dar las fichas")

    if cantidad <= 0:
        return respuesta_error("La cantidad debe ser mayor a 0")

    exito, mensaje = dar_fichas(sala_id, usuario_id, a_usuario_id, cantidad, motivo)

    if exito:
        return respuesta_ok({"message": mensaje})
    else:
        return respuesta_error(mensaje)


# ============================================
# Chat de la sala
# ============================================

@rooms_bp.route("/<int:sala_id>/chat", methods=["GET"])
def ver_chat(sala_id):
    """
    Obtiene los últimos mensajes del chat de una sala.
    Query param opcional: limit (por defecto 50)
    """
    limite = request.args.get("limit", 50, type=int)
    mensajes = obtener_mensajes(sala_id, limite)
    return respuesta_ok({"messages": mensajes})


@rooms_bp.route("/<int:sala_id>/chat", methods=["POST"])
@login_requerido
def enviar_chat(sala_id):
    """
    Envía un mensaje al chat de la sala.
    Recibe JSON: { mensaje }
    """
    usuario_id = session["user_id"]
    datos = request.get_json()

    if not datos or not datos.get("mensaje", "").strip():
        return respuesta_error("El mensaje no puede estar vacío")

    mensaje_texto = datos["mensaje"].strip()

    # Limitar la longitud del mensaje
    if len(mensaje_texto) > 500:
        return respuesta_error("El mensaje es demasiado largo (máximo 500 caracteres)")

    mensaje = enviar_mensaje(sala_id, usuario_id, mensaje_texto)

    if mensaje:
        return respuesta_ok({"message": mensaje})
    else:
        return respuesta_error("Error al enviar el mensaje", 500)


# ============================================
# Búsqueda por código de invitación
# ============================================

@rooms_bp.route("/join-code/<codigo>", methods=["GET"])
def buscar_por_codigo(codigo):
    """
    Busca una sala por su código de invitación.
    Útil para cuando un amigo comparte el código.
    """
    sala = obtener_sala_por_codigo(codigo.upper())

    if not sala:
        return respuesta_error("No se encontró ninguna sala con ese código", 404)

    return respuesta_ok({"room": sala})
