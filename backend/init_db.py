"""
init_db.py - Script para inicializar la base de datos.
Crea la base de datos, las tablas y un usuario demo.
Ejecutar una sola vez antes de arrancar el servidor.

Uso: python init_db.py
"""

import os
import mysql.connector
from werkzeug.security import generate_password_hash
from config import DB_HOST, DB_USER, DB_PASS, DB_NAME

# Fichas iniciales para el usuario demo
FICHAS_DEMO = 5000


def main():
    print("=" * 40)
    print("  BetM8 — Inicialización de Base de Datos")
    print("=" * 40)
    print()

    # --- Paso 1: Conectar a MySQL (sin seleccionar base de datos) ---
    print("Conectando a MySQL...")
    try:
        conexion = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS
        )
        cursor = conexion.cursor()
        print("✓ Conexión establecida")
    except Exception as e:
        print(f"✕ Error al conectar a MySQL: {e}")
        print()
        print("Verifica que MySQL esté corriendo y que las credenciales")
        print("en .env (o config.py) sean correctas.")
        return

    # --- Paso 2: Crear la base de datos ---
    print()
    print(f"Creando base de datos '{DB_NAME}'...")
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")
        print(f"✓ Base de datos '{DB_NAME}' lista")
    except Exception as e:
        print(f"✕ Error al crear la base de datos: {e}")
        conexion.close()
        return

    # --- Paso 3: Ejecutar el schema.sql ---
    print()
    print("Creando tablas...")
    try:
        # Leer el archivo schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), "database", "schema.sql")
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        # Ejecutar cada sentencia SQL por separado
        # (MySQL connector no soporta múltiples sentencias por defecto)
        sentencias = schema_sql.split(";")
        for sentencia in sentencias:
            sentencia = sentencia.strip()
            # Ignorar líneas vacías y comentarios
            if sentencia and not sentencia.startswith("--"):
                # Ignorar las sentencias CREATE DATABASE y USE (ya las hicimos)
                if sentencia.upper().startswith("CREATE DATABASE") or sentencia.upper().startswith("USE"):
                    continue
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
        conexion.close()
        return

    # --- Paso 4: Crear usuario demo ---
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

    # --- Finalizar ---
    conexion.close()
    print()
    print("=" * 40)
    print("  ¡Listo! Base de datos inicializada.")
    print("  Ahora puedes ejecutar: python app.py")
    print("=" * 40)


if __name__ == "__main__":
    main()
