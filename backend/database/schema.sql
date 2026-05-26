-- ============================================
-- schema.sql - Esquema de la base de datos BetM8
-- Ejecutar este archivo para crear todas las tablas.
-- Uso: mysql -u root -p < schema.sql
-- ============================================

-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS betm8;
USE betm8;

-- ============================================
-- Tabla: usuarios
-- Guarda la información de cada jugador registrado.
-- ============================================
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    coins INT DEFAULT 5000,
    xp INT DEFAULT 0,
    level INT DEFAULT 1,
    avatar VARCHAR(100) DEFAULT 'default',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    games_played INT DEFAULT 0,
    total_won INT DEFAULT 0
);

-- ============================================
-- Tabla: salas
-- Cada sala representa una mesa/partida donde
-- los jugadores se unen para jugar.
-- ============================================
CREATE TABLE IF NOT EXISTS salas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    juego VARCHAR(50) NOT NULL,
    host_id INT NOT NULL,
    tipo ENUM('publica', 'privada') DEFAULT 'publica',
    password VARCHAR(255) DEFAULT NULL,
    max_jugadores INT DEFAULT 4,
    fichas_inicio INT DEFAULT 100,
    estado ENUM('esperando', 'jugando', 'finalizada') DEFAULT 'esperando',
    codigo_inv VARCHAR(20) DEFAULT NULL,
    es_torneo BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (host_id) REFERENCES usuarios(id)
);

-- ============================================
-- Tabla: sala_jugadores
-- Relación entre salas y jugadores.
-- Guarda las fichas actuales de cada jugador en la sala.
-- ============================================
CREATE TABLE IF NOT EXISTS sala_jugadores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sala_id INT NOT NULL,
    usuario_id INT NOT NULL,
    fichas INT DEFAULT 100,
    unido_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (sala_id) REFERENCES salas(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- ============================================
-- Tabla: partidas
-- Registra cada ronda jugada dentro de una sala.
-- estado_json guarda el estado del juego en formato JSON.
-- ============================================
CREATE TABLE IF NOT EXISTS partidas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sala_id INT NOT NULL,
    ronda INT DEFAULT 1,
    iniciada_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finalizada_at TIMESTAMP NULL,
    estado_json JSON DEFAULT NULL,
    FOREIGN KEY (sala_id) REFERENCES salas(id)
);

-- ============================================
-- Tabla: transacciones
-- Historial de movimientos de monedas de cada jugador.
-- ============================================
CREATE TABLE IF NOT EXISTS transacciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    sala_id INT DEFAULT NULL,
    cantidad INT NOT NULL,
    tipo ENUM('apuesta', 'ganancia', 'bonus', 'compra') NOT NULL,
    descripcion VARCHAR(255) DEFAULT NULL,
    creado_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (sala_id) REFERENCES salas(id)
);

-- ============================================
-- Tabla: mensajes_chat
-- Mensajes del chat dentro de cada sala.
-- ============================================
CREATE TABLE IF NOT EXISTS mensajes_chat (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sala_id INT NOT NULL,
    usuario_id INT NOT NULL,
    mensaje TEXT NOT NULL,
    enviado_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sala_id) REFERENCES salas(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- ============================================
-- Tabla: estado_partida
-- Guarda el estado en tiempo real de una partida
-- multijugador. El campo estado es un JSON con
-- toda la info necesaria (cartas, turnos, etc).
-- ============================================
CREATE TABLE IF NOT EXISTS estado_partida (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sala_id INT NOT NULL,
    juego VARCHAR(20) NOT NULL,
    estado JSON NOT NULL COMMENT 'Estado completo de la partida en JSON',
    turno_usuario_id INT NULL COMMENT 'ID del jugador cuyo turno es ahora',
    fase VARCHAR(30) DEFAULT 'esperando' COMMENT 'esperando, jugando, finalizada',
    actualizado_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sala_id) REFERENCES salas(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
