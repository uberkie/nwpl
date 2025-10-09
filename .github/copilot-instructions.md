# Copilot Instructions for `nwpl`

## Project Overview
- Django 4.2 project in `network/` with single app `planning` providing templates, static assets, and data model for a network planning dashboard.
- ReactPy components live under two packages: legacy `reactpy-components/` (hyphenated) and compat shim `reactpy_components/` used by templates and ReactPy-Django loader.
- SQLite database (`db.sqlite3`) served via Django ORM; migrations live in `planning/migrations/`.

## Key Workflows
- Install deps with `pip install -r network/requirements.txt` (project expects a virtualenv at `network/.venv/`).
- Run dev server with `python network/manage.py runserver 0.0.0.0:8000`; ASGI uses `daphne` and integrates ReactPy websockets.
- Apply migrations using `python network/manage.py migrate` before running server.
- ReactPy components auto-register via `reactpy_django`; ensure module paths use `reactpy_components` (underscore) to avoid import failures.

## Architecture Details
- `planning/models.py`: `DeviceModel` records support dynamic catalogue in ReactPy UI (`device_models.py`).
- `planning/views.py`: Template-based views rendering `dashboard.html` and `device_model.html` (ReactPy hooks for UI).
- Templates pull components with `{% component "reactpy_components.dashboard.Dashboard" %}`; components re-exported from shim modules in `reactpy_components/`.
- `network/asgi.py`: Configures Channels `ProtocolTypeRouter` for HTTP + ReactPy websocket route; requires `daphne` during development.
- Static assets under `planning/static/css/`; ensure `collectstatic` considered if extending for production.

## Project Conventions
- ReactPy component logic resides in hyphenated package; avoid renaming directories. Use shim modules in `reactpy_components/` to expose underscore paths.
- Use Django templates primarily as ReactPy mount points; minimal server-side context.
- Maintain consistent data contracts between Django models and ReactPy state (e.g., `DeviceModel` fields mirrored by component props/state).
- When adding new ReactPy modules, create matching shim entries in `reactpy_components/` to keep `reactpy_django` import paths valid (e.g., `reactpy_components/device_models.py` re-exports `DeviceModelsAdmin` from `reactpy-components.device_models`).

## Troubleshooting
- If ReactPy components fail to register, verify matching module path in `reactpy_components/` and ensure `__init__.py` re-exports needed symbols.
- For database issues, check migrations in `planning/migrations/`; run `python network/manage.py makemigrations planning` and migrate.
- Websocket issues often linked to missing `daphne` or misconfigured ASGI route; confirm `reactpy_django` URLs included in `network/urls.py`.

## Helpful References
- `network/settings.py` for installed apps and static settings.
- `planning/templates/` to see template-to-component bindings.
- `reactpy-components/dashboard.py` for main UI logic and internal helper components.
