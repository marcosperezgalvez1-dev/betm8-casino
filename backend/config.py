"""
config.py - Configuración del servidor y base de datos.
Lee las variables de entorno del archivo .env (si existe),
y si no las encuentra usa valores por defecto para desarrollo.
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (si existe el archivo)
load_dotenv()

# --- Elegir entre SQLite (PythonAnywhere gratis) o MySQL (local/pro) ---
# Si USE_SQLITE=true se usa SQLite, que no necesita instalar nada extra.
USE_SQLITE = os.getenv("USE_SQLITE", "false").lower() == "true"

# --- Configuración de la base de datos MySQL ---
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_NAME = os.getenv("DB_NAME", "betm8")

# --- Clave secreta para sesiones y tokens ---
SECRET_KEY = os.getenv("SECRET_KEY", "betm8-secret-key-dev")
