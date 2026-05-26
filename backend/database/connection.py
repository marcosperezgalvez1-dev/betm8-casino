"""
connection.py - Conexión a la base de datos.
Soporta dos modos:
  - SQLite (para PythonAnywhere gratuito, no necesita instalar nada)
  - MySQL (para desarrollo local o servidores con MySQL)
Se elige con la variable de entorno USE_SQLITE=true/false.
"""

import os
import sqlite3
from config import USE_SQLITE, DB_HOST, DB_USER, DB_PASS, DB_NAME

# Ruta al archivo SQLite (se crea en la carpeta backend/)
SQLITE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "betm8.db")


class SQLiteConnection:
    """
    Wrapper alrededor de sqlite3 para que se comporte parecido a mysql.connector.
    Así no hay que cambiar los models que usan conexion.cursor(dictionary=True).
    """

    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")

    def cursor(self, dictionary=False):
        """Devuelve un cursor que convierte filas a diccionarios."""
        return SQLiteCursor(self.conn.cursor())

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def is_connected(self):
        return True


class SQLiteCursor:
    """
    Wrapper alrededor del cursor de SQLite.
    Convierte sqlite3.Row a diccionarios normales y adapta los placeholders.
    """

    def __init__(self, cursor):
        self.cursor = cursor
        self.lastrowid = None

    def execute(self, query, params=None):
        """Ejecuta una query adaptando %s a ? para SQLite."""
        # Adaptar placeholders de MySQL (%s) a SQLite (?)
        query = query.replace("%s", "?")
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        self.lastrowid = self.cursor.lastrowid

    def fetchone(self):
        """Devuelve una fila como diccionario o None."""
        row = self.cursor.fetchone()
        if row is None:
            return None
        return dict(row)

    def fetchall(self):
        """Devuelve todas las filas como lista de diccionarios."""
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]


def get_db():
    """
    Abre y devuelve una conexión a la base de datos.
    - Si USE_SQLITE=true: usa SQLite (archivo local betm8.db)
    - Si USE_SQLITE=false: usa MySQL (necesita mysql-connector-python)
    """
    if USE_SQLITE:
        return SQLiteConnection(SQLITE_PATH)
    else:
        import mysql.connector
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
    if conexion:
        if USE_SQLITE:
            conexion.close()
        else:
            if conexion.is_connected():
                conexion.close()
