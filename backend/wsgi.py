"""
wsgi.py - Punto de entrada para PythonAnywhere.
PythonAnywhere necesita este archivo para saber cómo arrancar la app Flask.
"""

import sys
import os

# Añadir la carpeta del backend al path de Python
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.insert(0, path)

# Cargar variables de entorno desde .env
from dotenv import load_dotenv
load_dotenv(os.path.join(path, '.env'))

# Importar la app de Flask (PythonAnywhere busca la variable 'application')
from app import app as application
