"""
app.py - Aplicación principal de Flask para BetM8.
Este archivo arranca el servidor, registra las rutas (blueprints)
y sirve los archivos del frontend.
"""

import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from config import SECRET_KEY

# Ruta a la carpeta del frontend (está un nivel arriba, en ../frontend/)
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

# --- Crear la aplicación Flask ---
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
app.secret_key = SECRET_KEY

# Habilitar CORS para permitir peticiones desde Arsys (producción) y localhost (desarrollo)
CORS(app, origins=[
    'http://localhost',
    'http://localhost:5000',
    'http://127.0.0.1',
    'https://ARSYS_DOMAIN.com'
], supports_credentials=True)

# --- Registrar los blueprints (rutas) ---
from routes.auth import auth_bp
from routes.rooms import rooms_bp
from routes.games import games_bp

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(rooms_bp, url_prefix="/api/rooms")
app.register_blueprint(games_bp, url_prefix="/api/games")


# --- Ruta principal: sirve el index.html del frontend ---
@app.route("/")
def index():
    """Sirve la página principal del frontend."""
    return send_from_directory(FRONTEND_DIR, "index.html")


# --- Arrancar el servidor ---
if __name__ == "__main__":
    print("=== Servidor BetM8 iniciado en http://localhost:5000 ===")
    app.run(debug=True, port=5000)
