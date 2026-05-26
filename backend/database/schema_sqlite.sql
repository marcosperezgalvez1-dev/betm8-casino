-- ============================================
-- schema_sqlite.sql - Esquema para SQLite
-- Mismo esquema que schema.sql pero adaptado
-- a la sintaxis de SQLite (sin ENUM, sin JSON nativo, etc).
-- Uso: se ejecuta desde init_db.py cuando USE_SQLITE=true
-- ============================================

-- Tabla: usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    coins INTEGER DEFAULT 5000,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    avatar TEXT DEFAULT 'default',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    games_played INTEGER DEFAULT 0,
    total_won INTEGER DEFAULT 0
);

-- Tabla: salas
CREATE TABLE IF NOT EXISTS salas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    juego TEXT NOT NULL,
    host_id INTEGER NOT NULL,
    tipo TEXT DEFAULT 'publica',
    password TEXT DEFAULT NULL,
    max_jugadores INTEGER DEFAULT 4,
    fichas_inicio INTEGER DEFAULT 100,
    estado TEXT DEFAULT 'esperando',
    codigo_inv TEXT DEFAULT NULL,
    es_torneo INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (host_id) REFERENCES usuarios(id)
);

-- Tabla: sala_jugadores
CREATE TABLE IF NOT EXISTS sala_jugadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sala_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    fichas INTEGER DEFAULT 100,
    unido_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo INTEGER DEFAULT 1,
    FOREIGN KEY (sala_id) REFERENCES salas(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabla: partidas
CREATE TABLE IF NOT EXISTS partidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sala_id INTEGER NOT NULL,
    ronda INTEGER DEFAULT 1,
    iniciada_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finalizada_at TIMESTAMP NULL,
    estado_json TEXT DEFAULT NULL,
    FOREIGN KEY (sala_id) REFERENCES salas(id)
);

-- Tabla: transacciones
CREATE TABLE IF NOT EXISTS transacciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    sala_id INTEGER DEFAULT NULL,
    cantidad INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    descripcion TEXT DEFAULT NULL,
    creado_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (sala_id) REFERENCES salas(id)
);

-- Tabla: mensajes_chat
CREATE TABLE IF NOT EXISTS mensajes_chat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sala_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    mensaje TEXT NOT NULL,
    enviado_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sala_id) REFERENCES salas(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabla: estado_partida
CREATE TABLE IF NOT EXISTS estado_partida (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sala_id INTEGER NOT NULL,
    juego TEXT NOT NULL,
    estado TEXT NOT NULL,
    turno_usuario_id INTEGER NULL,
    fase TEXT DEFAULT 'esperando',
    actualizado_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sala_id) REFERENCES salas(id)
);
