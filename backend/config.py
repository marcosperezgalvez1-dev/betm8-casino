"""
config.py - Configuración del servidor y base de datos.
Lee las variables de entorno del archivo .env (si existe),
y si no las encuentra usa valores por defecto para desarrollo.
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (si existe el archivo)
load_dotenv()

# --- Configuración de la base de datos PostgreSQL (Supabase) ---
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "")

# --- Clave secreta para sesiones y tokens ---
SECRET_KEY = os.getenv("SECRET_KEY", "betm8-secret-key-dev")
