"""
init_db.py - Script para inicializar la base de datos.
Crea las tablas y un usuario demo en PostgreSQL (Supabase).
Ejecutar una sola vez antes de arrancar el servidor.

Uso: python init_db.py
"""

import os
import psycopg2
import psycopg2.extras
from werkzeug.security import generate_password_hash
from config import DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME

# Fichas iniciales para el usuario demo
FICHAS_DEMO = 5000


def main():
    print("=" * 40)
    print("  BetM8 — Inicialización de Base de Datos")
    print("=" * 40)
    print()

    # --- Paso 1: Conectar a PostgreSQL (Supabase) ---
    print("Conectando a PostgreSQL...")
    try:
        conexion = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        cursor = conexion.cursor()
        print("✓ Conexión establecida")
    except Exception as e:
        print(f"✕ Error al conectar a PostgreSQL: {e}")
        print()
        print("Verifica que los datos de conexión en .env sean correctos")
        print("y que Supabase esté accesible.")
        return

    # --- Paso 2: Ejecutar el schema.sql ---
    print()
    print("Creando tablas...")
    try:
        # Leer el archivo schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), "database", "schema.sql")
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        # Ejecutar cada sentencia SQL por separado
        sentencias = schema_sql.split(";")
        for sentencia in sentencias:
            sentencia = sentencia.strip()
            # Ignorar líneas vacías y comentarios
            if sentencia and not sentencia.startswith("--"):
                cursor.execute(sentencia)

        conexion.commit()
        print("✓ Tablas creadas correctamente:")
        print("  - usuarios")
        print("  - salas")
        print("  - sala_jugadores")
        print("  - partidas")
        print("  - transacciones")
        print("  - mensajes_chat")
    except Exception as e:
        print(f"✕ Error al crear las tablas: {e}")
        conexion.rollback()
        conexion.close()
        return

    # --- Paso 3: Crear usuario demo ---
    print()
    print("Creando usuario demo...")
    try:
        # Verificar si ya existe
        cursor.execute("SELECT id FROM usuarios WHERE username = 'demo'")
        existe = cursor.fetchone()

        if existe:
            print("✓ Usuario demo ya existe (no se modificó)")
        else:
            password_hash = generate_password_hash("demo123")
            cursor.execute(
                """INSERT INTO usuarios (username, email, password_hash, coins)
                   VALUES (%s, %s, %s, %s)""",
                ("demo", "demo@betm8.com", password_hash, FICHAS_DEMO)
            )
            conexion.commit()
            print("✓ Usuario demo creado:")
            print("  - Username: demo")
            print("  - Password: demo123")
            print(f"  - Fichas: {FICHAS_DEMO}")
    except Exception as e:
        print(f"✕ Error al crear usuario demo: {e}")
        conexion.rollback()

    # --- Finalizar ---
    conexion.close()
    print()
    print("=" * 40)
    print("  ¡Listo! Base de datos inicializada.")
    print("  Ahora puedes ejecutar: python app.py")
    print("=" * 40)


if __name__ == "__main__":
    main()
