"""
connection.py - Conexión a la base de datos MySQL.
Proporciona funciones simples para abrir y cerrar la conexión.
"""

import mysql.connector
from config import DB_HOST, DB_USER, DB_PASS, DB_NAME


def get_db():
    """
    Abre y devuelve una conexión a la base de datos MySQL.
    Si la base de datos no existe todavía, dará error
    (hay que crearla primero con schema.sql).
    """
    conexion = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )
    return conexion


def close_db(conexion):
    """
    Cierra la conexión a la base de datos si está abierta.
    Siempre hay que cerrar la conexión cuando terminamos de usarla.
    """
    if conexion and conexion.is_connected():
        conexion.close()
