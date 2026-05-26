"""
connection.py - Conexión a la base de datos PostgreSQL (Supabase).
Proporciona funciones simples para abrir y cerrar la conexión.
Usa psycopg2 con RealDictCursor para devolver filas como diccionarios.
"""

import psycopg2
import psycopg2.extras
from config import DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME


def get_db():
    """
    Abre y devuelve una conexión a la base de datos PostgreSQL.
    Usa RealDictCursor para que los resultados vengan como diccionarios.
    """
    conexion = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        cursor_factory=psycopg2.extras.RealDictCursor
    )
    return conexion


def close_db(conexion):
    """
    Cierra la conexión a la base de datos si está abierta.
    Siempre hay que cerrar la conexión cuando terminamos de usarla.
    """
    if conexion and not conexion.closed:
        conexion.close()
