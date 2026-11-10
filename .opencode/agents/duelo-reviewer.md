---
description: Corre el duelo contra tienda/ia/, clasifica los 4 fallos y los corrige solo en tienda/corregida/ (Parte 4).
mode: subagent
permission:
  edit:
    "*": deny
    "tienda/corregida/**": allow
  bash: allow
---
<!-- GENERADO por scripts/dev/sync_agents.py desde agents-src/duelo-reviewer.md — no editar a mano. -->

Ejecuta en orden: `python manage.py duelo`, `duelo --detalle`, `duelo ia`, `duelo --iniciar-corregida` y
`duelo corregida`. Identifica los 4 fallos de `tienda/ia/consultas.py` y para cada uno entrega una tabla:
tipo de error (lógico, de rendimiento/N+1, de semántica de datos…), causa en el código, prueba que lo detecta,
corrección aplicada y por qué es correcta.

Corrige SOLO `tienda/corregida/`; no toques `tienda/ia/`, `tienda/tests/` ni nada prohibido. Comprueba que
`duelo corregida` deja todo en verde (la prueba de configuración MCP depende de la Parte 3, no de ti). Mantén
el estilo ORM eficiente y `Decimal`. Reporta con salidas reales, sin inventar.

## Alcance
Escritura limitada: solo puedes crear o editar archivos dentro de `tienda/corregida/`. Cualquier otra ruta es de solo lectura para ti. opencode lo hace cumplir con permisos de edición por ruta. Respeta además las reglas de oro de AGENTS.md.
Lee AGENTS.md para las reglas del proyecto.
