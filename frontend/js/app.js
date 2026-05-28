/* ============================================
   BetM8 — Lógica compartida de la aplicación

   PATRÓN: API-first con fallback a localStorage.

   Cuando Flask está corriendo, todas las operaciones
   (login, registro, salas, chat...) van contra la API REST.
   Si el servidor no responde (fetch falla), se usa
   localStorage como respaldo para que el frontend
   siga funcionando en modo "demo" sin backend.

   Las funciones async (login, register, etc.) intentan
   primero la API. Las funciones síncronas antiguas
   (loginUser, registerUser, getRooms) se mantienen
   como fallback y para compatibilidad.
   ============================================ */

// Base de la API — detecta entorno automáticamente:
// En local apunta a Flask en localhost:5000
// En producción (Arsys) apunta a PythonAnywhere
const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:5000'
  : 'https://marcosperezgalvezdev.pythonanywhere.com';

// Usuario en memoria (cache para no leer localStorage cada vez)
let _currentUser = null;

// ---- FUNCIÓN AUXILIAR PARA LLAMADAS A LA API ----
async function apiCall(url, method = 'GET', body = null) {
  /*
   * Hace una petición fetch a la API de Flask.
   * - credentials:'include' envía las cookies de sesión.
   * - Si el servidor responde, devuelve el JSON.
   * - Si el servidor está caído o hay error de red, devuelve null.
   *   Esto permite que el código que llama haga fallback a localStorage.
   */
  try {
    const opciones = {
      method,
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    };

    // Solo añadir body si hay datos y no es GET
    if (body && method !== 'GET') {
      opciones.body = JSON.stringify(body);
    }

    const respuesta = await fetch(API_BASE + url, opciones);
    const datos = await respuesta.json();
    return datos;
  } catch (error) {
    // Error de red (servidor caído, sin conexión, etc.)
    console.warn('API no disponible:', error.message);
    return null;
  }
}


// ---- OBJETO PRINCIPAL ----
const BetM8 = {

  // ============================================
  // AUTH — Funciones async que usan la API
  // ============================================

  async login(usernameOrEmail, password) {
    /*
     * Inicia sesión contra la API.
     * Si la API responde, guarda el usuario en memoria y localStorage (cache).
     * Si la API no responde, hace fallback a loginUser() con localStorage.
     */
    const resultado = await apiCall('/api/auth/login', 'POST', {
      username_or_email: usernameOrEmail,
      password: password,
    });

    // Si la API respondió
    if (resultado) {
      if (resultado.ok) {
        _currentUser = resultado.user;
        localStorage.setItem('betm8_user', JSON.stringify(resultado.user));
      }
      return resultado;
    }

    // Fallback a localStorage si la API no está disponible
    const fallback = this.loginUser(usernameOrEmail, password);
    if (fallback.ok) {
      _currentUser = fallback.user;
    }
    return fallback;
  },

  async register(data) {
    /*
     * Registra un usuario nuevo contra la API.
     * data = { username, email, password }
     * Si la API no responde, hace fallback a registerUser() con localStorage.
     */
    const resultado = await apiCall('/api/auth/register', 'POST', {
      username: data.username,
      email: data.email,
      password: data.password,
    });

    // Si la API respondió
    if (resultado) {
      if (resultado.ok) {
        _currentUser = resultado.user;
        localStorage.setItem('betm8_user', JSON.stringify(resultado.user));
      }
      return resultado;
    }

    // Fallback a localStorage
    const fallback = this.registerUser(data);
    if (fallback.ok) {
      _currentUser = fallback.user;
      this.setUser(fallback.user);
    }
    return fallback;
  },

  async logout() {
    /*
     * Cierra la sesión en la API y limpia localStorage.
     * Siempre redirige al login, haya o no API.
     */
    await apiCall('/api/auth/logout', 'POST');
    _currentUser = null;
    localStorage.removeItem('betm8_user');
    window.location.href = 'login.html';
  },

  async getMe() {
    /*
     * Obtiene los datos del usuario actual desde la API.
     * Si la API responde, actualiza la cache local.
     * Si no, devuelve lo que haya en localStorage.
     */
    const resultado = await apiCall('/api/auth/me');

    if (resultado && resultado.ok) {
      _currentUser = resultado.user;
      localStorage.setItem('betm8_user', JSON.stringify(resultado.user));
      return resultado.user;
    }

    // Fallback: devolver lo que haya en localStorage
    return this.getUser();
  },

  // ============================================
  // AUTH — Funciones síncronas (localStorage / fallback)
  // ============================================

  getUser() {
    /*
     * Devuelve el usuario actual de forma síncrona.
     * Primero intenta memoria, luego localStorage.
     * Se usa en partes del código que no pueden ser async (navbar, etc.)
     */
    if (_currentUser) return _currentUser;
    const u = localStorage.getItem('betm8_user');
    if (u) {
      _currentUser = JSON.parse(u);
      return _currentUser;
    }
    return null;
  },

  setUser(user) {
    /* Guarda el usuario en memoria y localStorage. */
    _currentUser = user;
    localStorage.setItem('betm8_user', JSON.stringify(user));
  },

  requireAuth() {
    /* Redirige a login si no hay usuario. Devuelve true/false. */
    if (!this.getUser()) {
      window.location.href = 'login.html';
      return false;
    }
    return true;
  },

  updateCoins(delta) {
    /* Actualiza las fichas del usuario localmente (para animaciones rápidas). */
    const user = this.getUser();
    if (!user) return;
    user.coins = Math.max(0, (user.coins || 0) + delta);
    this.setUser(user);
    this.renderNavbar();
    return user.coins;
  },

  // ---- Registro de usuarios en localStorage (fallback) ----
  getUsers() {
    const u = localStorage.getItem('betm8_users');
    return u ? JSON.parse(u) : [];
  },

  registerUser(data) {
    /* Registro con localStorage (fallback si no hay API). */
    const users = this.getUsers();
    if (users.find(u => u.username === data.username)) return { ok: false, error: 'El usuario ya existe' };
    if (users.find(u => u.email === data.email)) return { ok: false, error: 'El email ya está registrado' };
    const user = {
      id: 'u_' + Date.now(),
      username: data.username,
      email: data.email,
      password: data.password,
      coins: 5000,
      xp: 0,
      level: 1,
      avatar: data.username.slice(0, 2).toUpperCase(),
      createdAt: new Date().toISOString(),
      gamesPlayed: 0,
      totalWon: 0,
    };
    users.push(user);
    localStorage.setItem('betm8_users', JSON.stringify(users));
    return { ok: true, user };
  },

  loginUser(usernameOrEmail, password) {
    /* Login con localStorage (fallback si no hay API). */
    const users = this.getUsers();
    const user = users.find(u => (u.username === usernameOrEmail || u.email === usernameOrEmail) && u.password === password);
    if (!user) return { ok: false, error: 'Credenciales incorrectas' };
    this.setUser(user);
    return { ok: true, user };
  },

  // ============================================
  // SALAS — Funciones async que usan la API
  // ============================================

  async getRoomsFromAPI(filters = {}) {
    /*
     * Lista las salas desde la API con filtros opcionales.
     * filters = { game, type, status, search }
     * Si la API no responde, hace fallback a getRooms() (localStorage).
     */
    // Construir los query params a partir de los filtros
    const params = new URLSearchParams();
    if (filters.game) params.append('game', filters.game);
    if (filters.type) params.append('type', filters.type);
    if (filters.status) params.append('status', filters.status);
    if (filters.search) params.append('search', filters.search);

    const queryString = params.toString();
    const url = '/api/rooms/' + (queryString ? '?' + queryString : '');

    const resultado = await apiCall(url);

    if (resultado && resultado.ok) {
      return resultado.rooms;
    }

    // Fallback a localStorage
    return this.getRooms();
  },

  async createRoom(data) {
    /*
     * Crea una sala nueva contra la API.
     * data = { nombre, juego, tipo, password, max_jugadores, fichas_inicio, es_torneo }
     * Si la API no responde, usa la función de localStorage.
     */
    const resultado = await apiCall('/api/rooms/', 'POST', data);

    if (resultado) {
      return resultado;
    }

    // Fallback a localStorage
    const room = this._createRoomLocal(data);
    return { ok: true, room };
  },

  async getRoom(id) {
    /*
     * Obtiene el detalle de una sala desde la API.
     * Si la API no responde, busca en localStorage.
     */
    const resultado = await apiCall('/api/rooms/' + id);

    if (resultado && resultado.ok) {
      return resultado.room;
    }

    // Fallback a localStorage
    return this._getRoomLocal(id);
  },

  async joinRoom(roomId, password = null) {
    /*
     * Unirse a una sala mediante la API.
     * Si la API no responde, usa la lógica de localStorage.
     */
    const body = password ? { password } : {};
    const resultado = await apiCall('/api/rooms/' + roomId + '/join', 'POST', body);

    if (resultado) {
      return resultado;
    }

    // Fallback a localStorage
    return this._joinRoomLocal(roomId, password);
  },

  async leaveRoom(roomId) {
    /* Salir de una sala. */
    const resultado = await apiCall('/api/rooms/' + roomId + '/leave', 'POST');

    if (resultado) return resultado;
    return { ok: true, message: 'Has salido de la sala' };
  },

  async startGame(roomId) {
    /* Iniciar la partida (solo host). */
    const resultado = await apiCall('/api/rooms/' + roomId + '/start', 'POST');
    if (resultado) return resultado;
    return { ok: false, error: 'API no disponible' };
  },

  async pauseGame(roomId) {
    /* Pausar la partida (solo host). */
    const resultado = await apiCall('/api/rooms/' + roomId + '/pause', 'POST');
    if (resultado) return resultado;
    return { ok: false, error: 'API no disponible' };
  },

  async endGame(roomId) {
    /* Finalizar la partida (solo host). */
    const resultado = await apiCall('/api/rooms/' + roomId + '/end', 'POST');
    if (resultado) return resultado;
    return { ok: false, error: 'API no disponible' };
  },

  async kickPlayer(roomId, userId) {
    /* Expulsar jugador de la sala (solo host). */
    const resultado = await apiCall('/api/rooms/' + roomId + '/kick', 'POST', {
      usuario_id: userId,
    });
    if (resultado) return resultado;
    return { ok: false, error: 'API no disponible' };
  },

  async giveCoins(roomId, toUserId, amount, reason = 'reparto') {
    /* Repartir fichas a un jugador (solo host). */
    const resultado = await apiCall('/api/rooms/' + roomId + '/give-coins', 'POST', {
      a_usuario_id: toUserId,
      cantidad: amount,
      motivo: reason,
    });
    if (resultado) return resultado;
    return { ok: false, error: 'API no disponible' };
  },

  async getChat(roomId) {
    /* Obtener mensajes del chat de una sala. */
    const resultado = await apiCall('/api/rooms/' + roomId + '/chat');
    if (resultado && resultado.ok) return resultado.messages;
    return [];
  },

  async sendChat(roomId, message) {
    /* Enviar un mensaje al chat de una sala. */
    const resultado = await apiCall('/api/rooms/' + roomId + '/chat', 'POST', {
      mensaje: message,
    });
    if (resultado) return resultado;
    return { ok: false, error: 'API no disponible' };
  },

  async joinByCode(code) {
    /* Buscar una sala por código de invitación. */
    const resultado = await apiCall('/api/rooms/join-code/' + code);
    if (resultado) return resultado;
    return { ok: false, error: 'API no disponible' };
  },

  // ============================================
  // SALAS — Funciones localStorage (fallback)
  // ============================================

  getRooms() {
    /* Lee las salas de localStorage (modo demo sin backend). */
    const r = localStorage.getItem('betm8_rooms');
    return r ? JSON.parse(r) : this._defaultRooms();
  },

  saveRooms(rooms) {
    localStorage.setItem('betm8_rooms', JSON.stringify(rooms));
  },

  _createRoomLocal(data) {
    /* Crea una sala en localStorage (fallback). */
    const rooms = this.getRooms();
    const user = this.getUser();
    const room = {
      id: 'room_' + Date.now(),
      nombre: data.nombre || data.name,
      juego: data.juego || data.game,
      host: user?.username || 'Anónimo',
      host_id: user?.id,
      host_username: user?.username,
      jugadores: [{ usuario_id: user?.id, username: user?.username, fichas: data.fichas_inicio || 1000, avatar: user?.avatar }],
      max_jugadores: data.max_jugadores || data.maxPlayers || 8,
      fichas_inicio: data.fichas_inicio || data.startingCoins || 1000,
      tipo: data.tipo || data.type || 'publica',
      created_at: new Date().toISOString(),
      estado: 'esperando',
      codigo_inv: Math.random().toString(36).substring(2, 8).toUpperCase(),
      es_torneo: data.es_torneo || false,
      jugadores_actuales: 1,
    };
    rooms.push(room);
    this.saveRooms(rooms);
    return room;
  },

  _getRoomLocal(id) {
    /* Busca una sala en localStorage por ID. */
    return this.getRooms().find(r => r.id === id || r.id === String(id)) || null;
  },

  _joinRoomLocal(roomId, password) {
    /* Unirse a una sala en localStorage (fallback). */
    const rooms = this.getRooms();
    const room = rooms.find(r => r.id === roomId || r.id === String(roomId));
    const user = this.getUser();
    if (!room || !user) return { ok: false, error: 'Sala no encontrada' };
    if (room.estado === 'jugando' || room.status === 'playing') return { ok: false, error: 'La partida ya ha comenzado' };

    const jugadores = room.jugadores || room.players || [];
    const maxJugadores = room.max_jugadores || room.maxPlayers || 8;

    if (jugadores.length >= maxJugadores) return { ok: false, error: 'Sala llena' };
    if (room.password && room.password !== password) return { ok: false, error: 'Contraseña incorrecta' };

    const already = jugadores.find(p => (p.usuario_id || p.id) === user.id);
    if (already) return { ok: true, message: 'Ya estás en la sala' };

    jugadores.push({ usuario_id: user.id, username: user.username, fichas: room.fichas_inicio || room.startingCoins || 1000, avatar: user.avatar });
    room.jugadores = jugadores;
    room.jugadores_actuales = jugadores.length;

    const idx = rooms.findIndex(r => r.id === roomId || r.id === String(roomId));
    rooms[idx] = room;
    this.saveRooms(rooms);
    return { ok: true, message: 'Te has unido a la sala' };
  },

  updateRoom(id, patch) {
    /* Actualiza una sala en localStorage. */
    const rooms = this.getRooms();
    const idx = rooms.findIndex(r => r.id === id);
    if (idx === -1) return;
    rooms[idx] = { ...rooms[idx], ...patch };
    this.saveRooms(rooms);
    return rooms[idx];
  },

  // ============================================
  // NAVBAR
  // ============================================

  renderNavbar() {
    const nav = document.getElementById('betm8-nav');
    if (!nav) return;
    const user = this.getUser();
    const page = window.location.pathname.split('/').pop() || 'index.html';

    const links = [
      { href: 'index.html', label: 'Inicio' },
      { href: 'lobby.html', label: 'Salas' },
      { href: 'como-funciona.html', label: 'Cómo funciona' },
    ];

    nav.innerHTML = `
      <a class="navbar-brand" href="index.html">Bet<span>M8</span></a>
      <ul class="navbar-nav" id="nav-links">
        ${links.map(l => `<li><a href="${l.href}" class="${page === l.href ? 'active' : ''}">${l.label}</a></li>`).join('')}
      </ul>
      <div class="navbar-actions">
        ${user ? `
          <div class="navbar-coins">${(user.coins || 0).toLocaleString()}</div>
          <div class="navbar-user-wrap">
            <div class="navbar-avatar" title="${user.username}" onclick="BetM8.toggleUserDropdown(event)">${user.avatar || user.username.slice(0,2).toUpperCase()}</div>
            <div class="navbar-dropdown" id="user-dropdown">
              <button class="navbar-dropdown-item" onclick="BetM8.toast('Próximamente','info')">👤 Mi perfil</button>
              <div class="navbar-dropdown-sep"></div>
              <button class="navbar-dropdown-item danger" onclick="BetM8.logout()">🚪 Cerrar sesión</button>
            </div>
          </div>
        ` : `
          <a href="login.html" class="btn btn-ghost btn-sm">Iniciar sesión</a>
          <a href="register.html" class="btn btn-primary btn-sm">Registrarse</a>
        `}
        <button class="navbar-toggle" id="nav-toggle" onclick="BetM8.toggleMobileNav()">☰</button>
      </div>
    `;
  },

  toggleMobileNav() {
    const links = document.getElementById('nav-links');
    if (links) links.classList.toggle('open');
  },

  toggleUserDropdown(e) {
    e.stopPropagation();
    const dd = document.getElementById('user-dropdown');
    if (dd) dd.classList.toggle('open');
  },

  // ============================================
  // TOAST (notificaciones)
  // ============================================

  toast(msg, type = 'info', duration = 3000) {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    const icons = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.innerHTML = `<span>${icons[type] || 'ℹ'}</span><span>${msg}</span>`;
    container.appendChild(t);
    setTimeout(() => { t.style.opacity = '0'; t.style.transform = 'translateX(120%)'; t.style.transition = '0.3s'; setTimeout(() => t.remove(), 300); }, duration);
  },

  // ============================================
  // SALAS DEMO (localStorage)
  // ============================================

  _defaultRooms() {
    const rooms = [
      { id: 'room_demo1', nombre: 'Blackjack VIP', juego: 'blackjack', tipo: 'publica', host_username: 'CasinoKing', host_id: 'u_demo', jugadores: [{usuario_id:'u_d1',username:'CasinoKing',fichas:5000},{usuario_id:'u_d2',username:'LuckyStar',fichas:3200},{usuario_id:'u_d3',username:'PokerFace',fichas:1800}], max_jugadores: 6, fichas_inicio: 2000, created_at: new Date(Date.now()-300000).toISOString(), estado: 'jugando', codigo_inv: 'BJ1VIP', jugadores_actuales: 3 },
      { id: 'room_demo2', nombre: 'Ruleta Amigos', juego: 'ruleta', tipo: 'publica', host_username: 'SpinMaster', host_id: 'u_demo2', jugadores: [{usuario_id:'u_d4',username:'SpinMaster',fichas:8000},{usuario_id:'u_d5',username:'RedQueen',fichas:500}], max_jugadores: 8, fichas_inicio: 1000, created_at: new Date(Date.now()-120000).toISOString(), estado: 'esperando', codigo_inv: 'RUL123', jugadores_actuales: 2 },
      { id: 'room_demo3', nombre: 'Torneo Poker #1', juego: 'poker', tipo: 'privada', host_username: 'MarcosPro', host_id: 'u_demo3', jugadores: [{usuario_id:'u_d6',username:'MarcosPro',fichas:10000},{usuario_id:'u_d7',username:'Bluffer99',fichas:10000},{usuario_id:'u_d8',username:'AllInAlex',fichas:10000},{usuario_id:'u_d9',username:'SilentBob',fichas:10000}], max_jugadores: 8, fichas_inicio: 10000, created_at: new Date(Date.now()-600000).toISOString(), estado: 'esperando', codigo_inv: 'PKR001', es_torneo: true, jugadores_actuales: 4 },
      { id: 'room_demo4', nombre: 'Slots Fiesta', juego: 'slots', tipo: 'publica', host_username: 'SlotQueen', host_id: 'u_demo4', jugadores: [{usuario_id:'u_d10',username:'SlotQueen',fichas:750}], max_jugadores: 10, fichas_inicio: 500, created_at: new Date(Date.now()-60000).toISOString(), estado: 'esperando', codigo_inv: 'SLT777', jugadores_actuales: 1 },
      { id: 'room_demo5', nombre: 'Baccarat Exclusivo', juego: 'baccarat', tipo: 'privada', host_username: 'MrBig', host_id: 'u_demo5', jugadores: [{usuario_id:'u_d11',username:'MrBig',fichas:50000},{usuario_id:'u_d12',username:'LaadyLuck',fichas:25000}], max_jugadores: 4, fichas_inicio: 20000, created_at: new Date(Date.now()-900000).toISOString(), estado: 'esperando', codigo_inv: 'BAC999', jugadores_actuales: 2 },
    ];
    this.saveRooms(rooms);
    return rooms;
  },

  // ============================================
  // FORMATO Y UTILIDADES
  // ============================================

  formatCoins(n) { return Number(n).toLocaleString('es-ES'); },

  timeAgo(iso) {
    const diff = (Date.now() - new Date(iso)) / 1000;
    if (diff < 60) return 'hace un momento';
    if (diff < 3600) return `hace ${Math.floor(diff/60)}m`;
    if (diff < 86400) return `hace ${Math.floor(diff/3600)}h`;
    return `hace ${Math.floor(diff/86400)}d`;
  },
};

// Renderizar la navbar automáticamente al cargar la página
document.addEventListener('DOMContentLoaded', () => {
  BetM8.renderNavbar();
  document.addEventListener('click', () => {
    const dd = document.getElementById('user-dropdown');
    if (dd) dd.classList.remove('open');
  });
});
