# Cómo contribuir

## Flujo de ramas
`main` solo recibe `develop` al final. Cada tarea va en su rama desde `develop`
(`chore/…`, `feature/…`, `docs/…`) y entra por PR (`gh pr create --base develop`) con: qué, por qué, cómo se probó.
Pruebas en verde antes de mergear. No se reescribe el historial publicado.

## Commits
Conventional Commits, en español e imperativo: `feat:`, `fix:`, `test:`, `docs:`, `chore:`, `refactor:`.
Pequeños y atómicos. Cada integrante commitea con su propia identidad de git.

## Reglas de oro
- No modificar `tienda/tests/`, `tienda/ia/`, `tienda/models.py`, `cargar_datos`, `tiendactl.py`, `tienda/servidor_mcp.py`.
- CLI y MCP son de solo lectura: nunca escribir en la BD.
- No subir `myvenv/`, `db.sqlite3`, `__pycache__/`, `.env` ni secretos.
- Estilo: `ruff check .` y `ruff format --check .`; si cambias `agents-src/`, ejecuta `python scripts/dev/sync_agents.py`.
