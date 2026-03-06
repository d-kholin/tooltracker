# CLAUDE.md - Tool Tracker

## Project Overview

Flask-based tool lending tracker. Users log tools they own, lend them to people, and track loans/returns. Authentication is OIDC-only (designed for Authentik). Data is stored in SQLite with per-user isolation.

## Build & Run

### Docker (primary)
```bash
docker compose up --build
```
Runs on port 5000. Requires `.env` file with OIDC config (see Environment below).

### Direct Python
```bash
pip install -r requirements.txt
python app.py
```

### Linting
Uses [Trunk](https://trunk.io) for linting. Config at `.trunk/trunk.yaml`.
```bash
trunk check       # run all linters
trunk fmt          # auto-format
```
Enabled linters: black, isort, ruff, bandit, hadolint, prettier, markdownlint, yamllint, and others.

## Architecture

**Monolith** - three Python files, no blueprints:

| File | Purpose |
|------|---------|
| `app.py` | All routes, DB schema, template rendering (~1550 lines) |
| `auth.py` | OIDC auth flow, `User` model (Flask-Login), `auth_required` decorator |
| `config.py` | Config classes loaded from env vars, image optimization constants |

### Other files
- `templates/` - Jinja2 templates extending `base.html`
- `static/js/` - `app.js` (main), `lend.js` (lending UI), `brand-logos.js`
- `static/images/` - user-uploaded tool images
- `frontend/components/` - React JSX components (BottomNav, QuickAddTask, TaskCard)
- `migrate_tools.py` - one-off migration script
- `test_auth.py` - auth tests

## Database

Single SQLite file (`tooltracker.db` by default, configurable via `TOOLTRACKER_DB` env var).

### Schema

**users** - OIDC user accounts
- `id` TEXT PK (OIDC `sub` claim), `email`, `name`, `picture`, `created_at`, `last_login`

**tools** - tracked tools (per-user via `created_by`)
- `id` INTEGER PK, `name`, `description`, `value` REAL, `image_path`, `brand`, `model_number`, `serial_number`, `acquisition_date`, `created_by` FK->users

**people** - borrowers (per-user, unique name per user)
- `id` INTEGER PK, `name`, `contact_info`, `created_by` FK->users, UNIQUE(name, created_by)

**loans** - lending records
- `id` INTEGER PK, `tool_id` FK->tools, `person_id` FK->people, `lent_on`, `returned_on` (NULL=active), `lent_by` FK->users

## Key Patterns

### Per-user data isolation
All queries filter by `created_by = current_user.id`. Users only see their own tools, people, and loans. This is enforced at the query level, not middleware.

### Authentication
- OIDC-only, no local passwords. Configured for Authentik but works with any OIDC provider.
- `@auth_required` decorator on all protected routes (wraps Flask-Login's `@login_required`).
- OIDC discovery URL auto-configures endpoints; fallback to manual endpoint config.

### Image handling
- Tool images uploaded to `static/images/`, resized to max 1024px, JPEG quality 85.
- Uses Pillow for optimization. Max upload size 5MB.

### ProxyFix
App uses `werkzeug.middleware.proxy_fix.ProxyFix` for reverse proxy support (scheme/host detection).

## Route Organization

| Category | Routes |
|----------|--------|
| **Auth** | `/login`, `/oidc/callback`, `/logout` |
| **Health** | `/health` |
| **Dashboard** | `/` (index) |
| **Tools CRUD** | `/add`, `/edit/<id>`, `/delete/<id>`, `/tool/<id>` |
| **Tools API** | `/api/tools` (GET/POST), `/api/brands` (GET) |
| **People** | `/people`, `/add_person`, `/people/<id>`, `/people/<id>/edit`, `/people/<id>/delete` |
| **Lending** | `/lend/<id>`, `/return/<id>`, `/edit_loan/<id>` |
| **Reports** | `/report`, `/report/overdue`, `/report/financial`, `/brand-report` |
| **User** | `/user/settings`, `/user/export/tools`, `/user/import/tools`, `/user/download/template` |
| **Static** | `/data/images/<filename>` |

## Environment Variables

Required:
- `OIDC_CLIENT_ID` - OIDC client ID
- `OIDC_CLIENT_SECRET` - OIDC client secret
- `OIDC_REDIRECT_URI` - Full callback URL (e.g., `https://yourdomain.com/oidc/callback`)
- `OIDC_DISCOVERY_URL` - OIDC discovery endpoint (or set individual endpoints below)

Optional:
- `SECRET_KEY` - Flask secret key (auto-generated if not set)
- `TOOLTRACKER_DB` - SQLite DB path (default: `tooltracker.db`)
- `FLASK_ENV` - `development` or `production` (default: `development`)
- `APP_NAME` - Display name (default: `Tool Tracker`)
- `APP_URL` - Base URL (default: `http://localhost:5000`)
- `OIDC_SCOPES` - OIDC scopes (default: `openid profile email`)
- `OIDC_AUTHORIZATION_ENDPOINT`, `OIDC_TOKEN_ENDPOINT`, `OIDC_USERINFO_ENDPOINT` - Manual OIDC endpoints
