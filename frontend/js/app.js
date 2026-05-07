/* ============================================
   BetM8 — Shared Application Logic
   Simulated state management (localStorage)
   ============================================ */

// ---- STATE ----
const BetM8 = {

  // ---- USER ----
  getUser() {
    const u = localStorage.getItem('betm8_user');
    return u ? JSON.parse(u) : null;
  },

  setUser(user) {
    localStorage.setItem('betm8_user', JSON.stringify(user));
  },

  logout() {
    localStorage.removeItem('betm8_user');
    window.location.href = 'login.html';
  },

  requireAuth() {
    if (!this.getUser()) {
      window.location.href = 'login.html';
      return false;
    }
    return true;
  },

  updateCoins(delta) {
    const user = this.getUser();
    if (!user) return;
    user.coins = Math.max(0, (user.coins || 0) + delta);
    this.setUser(user);
    this.renderNavbar();
    return user.coins;
  },

  // ---- ROOMS ----
  getRooms() {
    const r = localStorage.getItem('betm8_rooms');
    return r ? JSON.parse(r) : this._defaultRooms();
  },

  saveRooms(rooms) {
    localStorage.setItem('betm8_rooms', JSON.stringify(rooms));
  },

  createRoom(data) {
    const rooms = this.getRooms();
    const user = this.getUser();
    const room = {
      id: 'room_' + Date.now(),
      ...data,
      host: user?.username || 'Anónimo',
      hostId: user?.id,
      players: [{ id: user?.id, username: user?.username, coins: data.startingCoins || 1000, avatar: user?.avatar }],
      maxPlayers: data.maxPlayers || 8,
      createdAt: new Date().toISOString(),
      status: 'waiting',
      chatMessages: [],
      tournamentBracket: data.isTournament ? [] : null,
    };
    rooms.push(room);
    this.saveRooms(rooms);
    return room;
  },

  getRoom(id) {
    return this.getRooms().find(r => r.id === id) || null;
  },

  updateRoom(id, patch) {
    const rooms = this.getRooms();
    const idx = rooms.findIndex(r => r.id === id);
    if (idx === -1) return;
    rooms[idx] = { ...rooms[idx], ...patch };
    this.saveRooms(rooms);
    return rooms[idx];
  },

  joinRoom(roomId, password = '') {
    const room = this.getRoom(roomId);
    const user = this.getUser();
    if (!room || !user) return { ok: false, msg: 'Sala no encontrada' };
    if (room.status === 'playing') return { ok: false, msg: 'La partida ya ha comenzado' };
    if (room.players.length >= room.maxPlayers) return { ok: false, msg: 'Sala llena' };
    if (room.password && room.password !== password) return { ok: false, msg: 'Contraseña incorrecta' };
    const already = room.players.find(p => p.id === user.id);
    if (already) return { ok: true, room };
    room.players.push({ id: user.id, username: user.username, coins: room.startingCoins || 1000, avatar: user.avatar });
    this.updateRoom(roomId, { players: room.players });
    return { ok: true, room };
  },

  // ---- USERS REGISTRY ----
  getUsers() {
    const u = localStorage.getItem('betm8_users');
    return u ? JSON.parse(u) : [];
  },

  registerUser(data) {
    const users = this.getUsers();
    if (users.find(u => u.username === data.username)) return { ok: false, msg: 'El usuario ya existe' };
    if (users.find(u => u.email === data.email)) return { ok: false, msg: 'El email ya está registrado' };
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
    const users = this.getUsers();
    const user = users.find(u => (u.username === usernameOrEmail || u.email === usernameOrEmail) && u.password === password);
    if (!user) return { ok: false, msg: 'Credenciales incorrectas' };
    this.setUser(user);
    return { ok: true, user };
  },

  // ---- NAVBAR RENDER ----
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
          <div class="navbar-avatar" title="${user.username}" onclick="BetM8.logout()">${user.avatar || user.username.slice(0,2).toUpperCase()}</div>
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

  // ---- TOAST ----
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

  // ---- DEFAULT ROOMS ----
  _defaultRooms() {
    const rooms = [
      { id: 'room_demo1', name: 'Blackjack VIP', game: 'blackjack', gameLabel: 'Blackjack', type: 'public', password: '', host: 'CasinoKing', hostId: 'u_demo', players: [{id:'u_d1',username:'CasinoKing',coins:5000},{id:'u_d2',username:'LuckyStar',coins:3200},{id:'u_d3',username:'PokerFace',coins:1800}], maxPlayers: 6, startingCoins: 2000, createdAt: new Date(Date.now()-300000).toISOString(), status: 'playing', chatMessages: [] },
      { id: 'room_demo2', name: 'Ruleta Amigos', game: 'ruleta', gameLabel: 'Ruleta', type: 'public', password: '', host: 'SpinMaster', hostId: 'u_demo2', players: [{id:'u_d4',username:'SpinMaster',coins:8000},{id:'u_d5',username:'RedQueen',coins:500}], maxPlayers: 8, startingCoins: 1000, createdAt: new Date(Date.now()-120000).toISOString(), status: 'waiting', chatMessages: [] },
      { id: 'room_demo3', name: 'Torneo Poker #1', game: 'poker', gameLabel: 'Poker', type: 'private', password: '1234', host: 'MarcosPro', hostId: 'u_demo3', players: [{id:'u_d6',username:'MarcosPro',coins:10000},{id:'u_d7',username:'Bluffer99',coins:10000},{id:'u_d8',username:'AllInAlex',coins:10000},{id:'u_d9',username:'SilentBob',coins:10000}], maxPlayers: 8, startingCoins: 10000, createdAt: new Date(Date.now()-600000).toISOString(), status: 'waiting', isTournament: true, chatMessages: [] },
      { id: 'room_demo4', name: 'Slots Fiesta', game: 'slots', gameLabel: 'Tragaperras', type: 'public', password: '', host: 'SlotQueen', hostId: 'u_demo4', players: [{id:'u_d10',username:'SlotQueen',coins:750}], maxPlayers: 10, startingCoins: 500, createdAt: new Date(Date.now()-60000).toISOString(), status: 'waiting', chatMessages: [] },
      { id: 'room_demo5', name: 'Baccarat Exclusivo', game: 'baccarat', gameLabel: 'Baccarat', type: 'private', password: 'vip', host: 'MrBig', hostId: 'u_demo5', players: [{id:'u_d11',username:'MrBig',coins:50000},{id:'u_d12',username:'LaadyLuck',coins:25000}], maxPlayers: 4, startingCoins: 20000, createdAt: new Date(Date.now()-900000).toISOString(), status: 'waiting', chatMessages: [] },
    ];
    this.saveRooms(rooms);
    return rooms;
  },

  // ---- FORMAT ----
  formatCoins(n) { return Number(n).toLocaleString('es-ES'); },
  timeAgo(iso) {
    const diff = (Date.now() - new Date(iso)) / 1000;
    if (diff < 60) return 'hace un momento';
    if (diff < 3600) return `hace ${Math.floor(diff/60)}m`;
    if (diff < 86400) return `hace ${Math.floor(diff/3600)}h`;
    return `hace ${Math.floor(diff/86400)}d`;
  },
};

// Auto-render navbar on load
document.addEventListener('DOMContentLoaded', () => BetM8.renderNavbar());
