# BetM8 — Casino Social Online

Casino online con dinero simulado para jugar con amigos en salas privadas.
No se usa dinero real. Crea una sala, invita a tus amigos con un codigo y jugad juntos a blackjack, ruleta, poker, slots, baccarat o dados.

## Requisitos

- **Python** 3.8 o superior
- **MySQL** 8.0 o superior
- **Navegador** moderno (Chrome, Firefox, Edge)

## Instalacion y ejecucion

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/casino-online.git
cd casino-online
```

### 2. Instalar MySQL

Descarga MySQL desde https://dev.mysql.com/downloads/ e instalalo.
Asegurate de tener un usuario con permisos (por defecto se usa `root` sin contraseña).

### 3. Instalar dependencias de Python

```bash
cd backend
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita el archivo `.env` si tu MySQL usa un usuario o contraseña diferente:

```
DB_HOST=localhost
DB_USER=root
DB_PASS=tu_contraseña
DB_NAME=betm8
SECRET_KEY=betm8-secret-key-dev
```

### 5. Inicializar la base de datos

```bash
python init_db.py
```

Esto crea la base de datos `betm8`, todas las tablas y un usuario demo.

### 6. Arrancar el servidor

```bash
python app.py
```

El servidor arranca en **http://localhost:5000**. Abre esa URL en tu navegador.

## Uso sin backend (modo demo)

Si no tienes MySQL instalado, puedes abrir directamente `frontend/index.html` en el navegador. El frontend funciona con localStorage como almacenamiento local (modo demo con datos ficticios).

## Credenciales demo

| Usuario | Contraseña |
|---------|-----------|
| demo    | demo123   |

## Estructura del proyecto

```
casino-online/
├── README.md
├── CLAUDE.md
├── .gitignore
├── frontend/
│   ├── index.html          # Landing page
│   ├── login.html          # Inicio de sesion
│   ├── register.html       # Registro
│   ├── lobby.html          # Lobby de salas
│   ├── crear-sala.html     # Crear sala privada
│   ├── gestion-sala.html   # Panel de gestion (host)
│   ├── como-funciona.html  # Explicacion del sitio
│   ├── blackjack.html      # Juego: Blackjack
│   ├── ruleta.html         # Juego: Ruleta
│   ├── poker.html          # Juego: Poker Texas Hold'em
│   ├── slots.html          # Juego: Tragaperras
│   ├── baccarat.html       # Juego: Baccarat
│   ├── dados.html          # Juego: Dados (Craps)
│   ├── css/global.css      # Sistema de diseno compartido
│   └── js/app.js           # Logica compartida (API + fallback localStorage)
└── backend/
    ├── app.py              # Servidor Flask principal
    ├── config.py           # Configuracion (BD, secretos)
    ├── init_db.py          # Script para crear la BD
    ├── requirements.txt    # Dependencias Python
    ├── .env.example        # Variables de entorno (plantilla)
    ├── database/
    │   ├── connection.py   # Conexion a MySQL
    │   └── schema.sql      # Esquema de tablas
    ├── routes/
    │   ├── auth.py         # Rutas de autenticacion
    │   ├── rooms.py        # Rutas de salas
    │   └── games.py        # Rutas de juegos (pendiente)
    ├── models/
    │   ├── user.py         # Funciones de usuario
    │   ├── room.py         # Funciones de salas
    │   └── chat.py         # Funciones de chat
    └── utils/
        └── helpers.py      # Utilidades (respuestas, decoradores)
```

## Stack tecnologico

- **Frontend:** HTML5 + CSS3 + JavaScript vanilla (sin frameworks)
- **Backend:** Python con Flask
- **Base de datos:** MySQL
- **Sesiones:** Flask session (cookies)
- **Passwords:** Hasheadas con Werkzeug (PBKDF2)

## Juegos disponibles

| Juego | Descripcion |
|-------|-------------|
| Blackjack | Clasico 21 contra el dealer |
| Ruleta | Ruleta europea con todas las apuestas |
| Poker | Texas Hold'em simplificado |
| Tragaperras | Slots con 3 carretes y multiplicadores |
| Baccarat | Punto y banca |
| Dados | Craps con 6 tipos de apuesta |
