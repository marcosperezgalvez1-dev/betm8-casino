# BetM8 — Casino Social Online

## Descripcion del Proyecto
Casino online con dinero simulado para jugar en salas privadas con amigos.
No se usa dinero real. Experiencia social de casino donde grupos de amigos
crean salas privadas y juegan juntos.

## Stack Tecnologico
- **Frontend:** HTML5, CSS3, JavaScript vanilla (sin frameworks)
- **Backend:** Python con Flask (pendiente)
- **Base de datos:** MySQL (pendiente)
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
- `js/app.js` — logica compartida: objeto BetM8 (auth con localStorage, gestion salas, navbar, toasts)

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
│   ├── gestion-sala.html   # Gestion de sala
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
│       └── app.js          # Logica compartida (objeto BetM8)
└── backend/                # Flask + MySQL (pendiente)
```

## Paginas
| Pagina | Archivo | Estado |
|--------|---------|--------|
| Landing | index.html | Pendiente (diseno listo) |
| Login | login.html | Pendiente (diseno listo) |
| Registro | register.html | Pendiente (diseno listo) |
| Lobby | lobby.html | Pendiente (diseno listo) |
| Crear Sala | crear-sala.html | Pendiente (diseno listo) |
| Gestion Sala | gestion-sala.html | Pendiente (diseno listo) |
| Como Funciona | como-funciona.html | Pendiente (diseno listo) |
| Blackjack | blackjack.html | Pendiente (diseno listo) |
| Ruleta | ruleta.html | Pendiente (diseno listo) |
| Poker | poker.html | Pendiente (diseno listo) |
| Slots | slots.html | Pendiente (diseno listo) |
| Baccarat | baccarat.html | Pendiente (diseno listo) |
| Dados | dados.html | Pendiente (diseno listo) |

## Estado Actual
- **Fecha inicio:** 2026-04-30
- **Fase:** Implementacion del frontend (disenos listos, pasando uno a uno)
- **Backend:** Pendiente — Flask + MySQL reemplazara localStorage

## Convenciones de Codigo
- Comentarios y nombres en espanol
- Codigo nivel junior, simple y legible
- Sin frameworks JS, sin preprocesadores CSS
- Variables y funciones con nombres claros

## Reglas de Colaboracion
1. Autorizacion previa antes de crear/modificar archivos
2. Trabajo incremental, una pagina a la vez
3. Resumenes breves al terminar cada tarea
4. Codigo nivel junior, simple y legible
5. GitHub: pedir permiso antes de commit/push
