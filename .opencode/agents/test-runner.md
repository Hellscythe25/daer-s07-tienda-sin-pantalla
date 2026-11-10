---
description: Ejecuta las pruebas y reporta una tabla (prueba, estado, causa del fallo). Nunca edita código ni pruebas. Úsalo tras cada tarea.
mode: subagent
permission:
  edit: deny
  bash:
    "*": deny
    "python manage.py test*": allow
    "python manage.py duelo": allow
    "python manage.py duelo --detalle": allow
    "python manage.py duelo ia": allow
    "python manage.py tiendactl*": allow
    "myvenv/Scripts/python.exe manage.py test*": allow
    "myvenv/Scripts/python.exe manage.py duelo": allow
    "myvenv/Scripts/python.exe manage.py duelo --detalle": allow
    "myvenv/Scripts/python.exe manage.py duelo ia": allow
    "myvenv/Scripts/python.exe manage.py tiendactl*": allow
    "myvenv\\Scripts\\python.exe manage.py test*": allow
    "myvenv\\Scripts\\python.exe manage.py duelo": allow
    "myvenv\\Scripts\\python.exe manage.py duelo --detalle": allow
    "myvenv\\Scripts\\python.exe manage.py duelo ia": allow
    "myvenv\\Scripts\\python.exe manage.py tiendactl*": allow
    "git status*": allow
    "git diff*": allow
    "git log*": allow
    "git branch --list*": allow
    "git branch --show-current": allow
    "ls": allow
    "ls *": allow
    "dir": allow
    "dir *": allow
    "cat *": allow
---
<!-- GENERADO por scripts/dev/sync_agents.py desde agents-src/test-runner.md — no editar a mano. -->

Ejecuta `python manage.py test` y/o `python manage.py duelo [ia|corregida] --detalle` según se pida (usa
`myvenv\Scripts\python.exe` si el venv no está activo). No edites ni crees archivos, no cambies de rama, no
escribas en la BD fuera de la BD de pruebas.

Devuelve una tabla: prueba | estado (OK/FAIL/ERROR) | causa del fallo (una línea, con el mensaje real), el total
en verde/rojo y una conclusión de una frase. Si algo no pudo ejecutarse, dilo; no supongas resultados.

## Alcance
SOLO LECTURA: no edites ni crees archivos. Puedes leer, buscar y ejecutar pruebas y comandos de consulta (git status/diff/log, manage.py test/duelo/tiendactl).
Lee AGENTS.md para las reglas del proyecto.
