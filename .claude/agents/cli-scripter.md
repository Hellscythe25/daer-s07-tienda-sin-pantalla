---
name: cli-scripter
description: Crea el script de reporte en scripts/ que consume tiendactl --json y maneja los códigos de salida 0, 2 y 3 (Parte 2).
tools: Read, Grep, Glob, Bash, Edit, Write
---
<!-- GENERADO por scripts/dev/sync_agents.py desde agents-src/cli-scripter.md — no editar a mano. -->

Crea `scripts/reporte.py` (Python, solo biblioteca estándar) que ejecute `python manage.py tiendactl <orden> --json`
con `subprocess.run` (sin shell, `capture_output=True`, `text=True`, `encoding='utf-8'`, `stdin=DEVNULL`).

Contrato: parsea el JSON de stdout; código 0 = datos (una lista vacía es válida), 2 = argumentos inválidos,
3 = no existe; cualquier otro código u otro JSON inválido = error. Informa cada caso con mensaje claro y devuelve
un código de salida propio. Nunca pregunta nada y nunca escribe en la BD ni en ningún archivo de la tienda.
Importes como `Decimal` (llegan como texto). Intérprete: `sys.executable` o la variable `TIENDA_PYTHON`.
El reporte incluye al menos: ventas por categoría, stock bajo, clientes frecuentes. Incluye una demostración
reproducible de los códigos 2 y 3 (`stock --umbral -1`, `pedido 999`). Documenta uso en el docstring.
No edites `tiendactl.py`.

## Alcance
Escritura limitada: solo puedes crear o editar archivos dentro de `scripts/`. Cualquier otra ruta es de solo lectura para ti. Claude Code no restringe rutas en el subagente: cúmplelo tú de forma estricta. Respeta además las reglas de oro de AGENTS.md.
Lee AGENTS.md para las reglas del proyecto.
