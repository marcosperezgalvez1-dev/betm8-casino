# BetM8 — Casino Social Online

## Descripcion del Proyecto
Casino online con dinero simulado para jugar en salas privadas con amigos.
No se usa dinero real. Experiencia social de casino donde grupos de amigos
crean salas privadas y juegan juntos.

## Stack Tecnologico
- **Frontend:** HTML5, CSS3, JavaScript vanilla (sin frameworks)
- **Backend:** Python con Flask
- **Base de datos:** MySQL
- **Sesiones:** Flask session (cookies)
- **Control de versiones:** Git + GitHub

## Estetica
- **Tema:** Dark / Gold / Neon
- **Fondo principal:** #0a0a0f
- **Dorado:** #d4a843
- **Acentos:** Verdes y azules neon
- **Fuentes:** Rajdhani (display) + Inter (body) via Google Fonts

## Sistema de Diseno
- `css/global.css` — sistema de diseno compartido (variables, reset, componentes base)
- Estilos especificos de cada pagina van en `<style>` dentro de cada HTML
- `js/app.js` — logica compartida: objeto BetM8 (API fetch + fallback localStorage, auth, salas, navbar, toasts)

## Arquitectura Frontend-Backend
- El frontend usa funciones async que llaman a la API REST de Flask
- Si la API no responde (servidor caido), se usa localStorage como fallback
- Flask sirve los archivos estaticos del frontend desde la ruta raiz /
- Las rutas API estan bajo /api/auth/, /api/rooms/, /api/games/
- Sesiones con cookies (flask session), no JWT

## Estructura de Carpetas
```
casino-online/
├── CLAUDE.md
├── README.md
├── .gitignore
├── frontend/
│   ├── index.html          # Landing page
│   ├── login.html          # Inicio de sesion
│   ├── register.html       # Registro
│   ├── lobby.html          # Lobby principal
│   ├── crear-sala.html     # Crear sala privada
│   ├── gestion-sala.html   # Gestion de sala (panel host)
│   ├── como-funciona.html  # Explicacion del sitio
│   ├── blackjack.html      # Juego: Blackjack
│   ├── ruleta.html         # Juego: Ruleta
│   ├── poker.html          # Juego: Poker
│   ├── slots.html          # Juego: Tragamonedas
│   ├── baccarat.html       # Juego: Baccarat
│   ├── dados.html          # Juego: Dados
│   ├── css/
│   │   └── global.css      # Sistema de diseno compartido
│   └── js/
│       └── app.js          # Logica compartida (API + fallback)
└── backend/
    ├── app.py              # Aplicacion Flask principal
    ├── config.py           # Configuracion (BD, secretos, .env)
    ├── init_db.py          # Script para crear BD y tablas
    ├── requirements.txt    # Dependencias Python
    ├── .env.example        # Plantilla de variables de entorno
    ├── database/
    │   ├── connection.py   # get_db() y close_db()
    │   └── schema.sql      # Esquema SQL (6 tablas)
    ├── routes/
    │   ├── auth.py         # Blueprint: registro, login, logout, me
    │   ├── rooms.py        # Blueprint: CRUD salas, chat, gestion
    │   └── games.py        # Blueprint: logica de juegos (pendiente)
    ├── models/
    │   ├── user.py         # Funciones de usuario (crear, buscar, coins)
    │   ├── room.py         # Funciones de salas (crear, listar, unirse...)
    │   └── chat.py         # Funciones de chat (enviar, obtener)
    └── utils/
        └── helpers.py      # respuesta_ok/error, decorador login_requerido
```

## Base de Datos (MySQL)
6 tablas:
- **usuarios** — datos de jugadores (coins, xp, level, avatar)
- **salas** — mesas de juego (juego, host, tipo, estado, codigo_inv)
- **sala_jugadores** — relacion jugador-sala con fichas
- **partidas** — rondas jugadas (estado_json)
- **transacciones** — historial de movimientos de fichas
- **mensajes_chat** — chat por sala

## API REST
- `POST /api/auth/register` — registro
- `POST /api/auth/login` — login
- `POST /api/auth/logout` — cerrar sesion
- `GET /api/auth/me` — usuario actual
- `GET /api/rooms/` — listar salas (con filtros)
- `POST /api/rooms/` — crear sala
- `GET /api/rooms/<id>` — detalle de sala
- `POST /api/rooms/<id>/join` — unirse
- `POST /api/rooms/<id>/leave` — salir
- `POST /api/rooms/<id>/start|pause|end` — gestion partida
- `POST /api/rooms/<id>/kick` — expulsar
- `POST /api/rooms/<id>/give-coins` — repartir fichas
- `GET/POST /api/rooms/<id>/chat` — leer/enviar mensajes
- `GET /api/rooms/join-code/<codigo>` — buscar por codigo

## Arquitectura de Despliegue
- **Frontend:** Arsys (hosting estatico — HTML/CSS/JS)
- **Backend:** PythonAnywhere (Flask API via wsgi.py)
- **Base de datos:** Supabase (PostgreSQL)
- **URLs producción:**
  - API: https://marcosperezgalvezdev.pythonanywhere.com
  - Frontend: https://betm8.es / https://www.betm8.es

## Estado Actual
- **Fecha inicio:** 2026-04-30
- **Fase:** Backend completo, frontend conectado, preparado para despliegue
- **Frontend:** Completo (13 paginas, 6 juegos funcionales)
- **Backend:** Completo (auth, salas, chat, modelos, BD, wsgi.py)
- **Conexion:** Frontend usa API con fallback a localStorage
- **Pendiente:** Testing end-to-end, despliegue final, logica multijugador en tiempo real

## Convenciones de Codigo
- Comentarios y nombres en espanol
- Codigo nivel junior, simple y legible
- Sin frameworks JS, sin preprocesadores CSS
- Variables y funciones con nombres claros
- Backend: try/except en queries, funciones puras en models/

## Reglas de Colaboracion
1. Autorizacion previa antes de crear/modificar archivos
2. Trabajo incremental, una pagina a la vez
3. Resumenes breves al terminar cada tarea
4. Codigo nivel junior, simple y legible
5. GitHub: pedir permiso antes de commit/push
