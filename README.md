# Lab extra S07 — La tienda sin pantalla: ORM para una CLI y un servidor MCP

Hasta ahora la tienda tenía pantallas: el admin (S05) y la vitrina (S06). Esta semana la usan **programas**:

- una **CLI headless** (`tiendactl`): para scripts, tareas programadas y otros sistemas;
- un **servidor MCP**: para que un **agente de IA** (Claude Code, VS Code, opencode/TecsupCode…) consulte
  la tienda con herramientas, sin SQL y sin poder escribir.

Los dos usan **las mismas seis consultas del ORM**, que son las que ustedes escriben (en pareja). Si una consulta
está mal, la respuesta está mal en la terminal, en el script y en lo que el agente le cuenta a una persona.

1. **Parte 1:** las seis consultas del ORM (`tienda/alumno/consultas.py`).
2. **Parte 2:** usar la CLI como lo haría un programa: `--json`, códigos de salida y un script de reporte.
3. **Parte 3:** conectar el servidor MCP a un cliente, hacerle preguntas al agente y ver qué hace con un dato
   que «da órdenes».
4. **Parte 4:** el duelo. Las mismas pruebas contra unas consultas que escribió una IA, con cuatro fallos.

La guía de laboratorio tiene el paso a paso.

## Empezar

Un integrante copia este repositorio con **Use this template** y agrega al otro como colaborador.

```powershell
python -m venv myvenv
myvenv\Scripts\activate
pip install -r requirements.txt       # Django y el SDK oficial de MCP para Python
python manage.py migrate
python manage.py cargar_datos         # datos FIJOS: cada pregunta tiene una respuesta conocida
python manage.py duelo                # casi todo en rojo: es lo esperado
```

## La CLI (Parte 2)

```powershell
python manage.py tiendactl categoria gaseosas
python manage.py tiendactl buscar chocolate --json
python manage.py tiendactl stock --umbral 5
python manage.py tiendactl ventas
python manage.py tiendactl clientes --minimo 2
python manage.py tiendactl pedido 1 --json
```

El contrato *headless*:
- con `--json` la salida es **solo** JSON;
- código de salida **0** si va bien, **2** si los argumentos no valen, **3** si no existe (en PowerShell se ve
  con `$LASTEXITCODE`);
- nunca pregunta nada y nunca escribe en la base de datos.

## El servidor MCP (Parte 3)

`python manage.py servidor_mcp` arranca el servidor por **stdio**. No se ejecuta a mano: lo lanza el cliente.
Tiene seis herramientas (`tienda_*`), todas de **solo lectura**. La configuración depende del cliente; usen la
del suyo y súbanla al repositorio. Comprueben el formato exacto en la documentación de su cliente: estos son los
de referencia.

**Claude Code** (`.mcp.json` en la raíz del proyecto; también `claude mcp add --scope project tienda -- myvenv\Scripts\python.exe manage.py servidor_mcp`):

```json
{
  "mcpServers": {
    "tienda": {"command": "myvenv/Scripts/python.exe", "args": ["manage.py", "servidor_mcp"]}
  }
}
```

**VS Code** (`.vscode/mcp.json`):

```json
{
  "servers": {
    "tienda": {"type": "stdio", "command": "${workspaceFolder}/myvenv/Scripts/python.exe",
               "args": ["${workspaceFolder}/manage.py", "servidor_mcp"]}
  }
}
```

**opencode / TecsupCode** (`opencode.json`):

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "tienda": {"type": "local", "command": ["myvenv/Scripts/python.exe", "manage.py", "servidor_mcp"], "enabled": true}
  }
}
```

**Sin agente** (necesita Node.js): `npx @modelcontextprotocol/inspector myvenv\Scripts\python.exe manage.py servidor_mcp`
abre una página donde se listan las herramientas y se llaman a mano.

## Comandos del duelo

| Comando | Para qué |
|---|---|
| `python manage.py duelo` | Corre las pruebas contra **sus** consultas y resume por parte |
| `python manage.py duelo --detalle` | Además, el error de cada prueba en rojo |
| `python manage.py duelo ia` | Las mismas pruebas contra las consultas de la IA (Parte 4) |
| `python manage.py duelo --iniciar-corregida` | Copia `tienda/ia/` a `tienda/corregida/` para corregirla |
| `python manage.py duelo corregida` | Las pruebas contra su copia corregida |

Para usar la CLI o el servidor con otra versión de las consultas: `$env:TIENDA_VERSION = "ia"` (y
`Remove-Item Env:TIENDA_VERSION` para volver a la suya).

## Estructura

| Carpeta o archivo | Qué es | ¿Lo editan? |
|---|---|---|
| `tienda/alumno/consultas.py` | **Sus seis consultas** (Parte 1) | Sí |
| `scripts/` | Su script de reporte (Parte 2) | Sí (lo crean) |
| `.mcp.json`, `.vscode/mcp.json` u `opencode.json` | La configuración de su cliente MCP (Parte 3) | Sí (la crean) |
| `tienda/ia/consultas.py` | Las consultas que escribió un asistente de IA | **No** |
| `tienda/corregida/` | Su copia de la de la IA, corregida (la crea `duelo --iniciar-corregida`) | Sí (Parte 4) |
| `tienda/tests/` | Las pruebas: el oráculo del laboratorio | **No** |
| `tienda/management/commands/tiendactl.py` | La CLI | No |
| `tienda/servidor_mcp.py` | El servidor MCP | No (léanlo) |
| `tienda/models.py`, `cargar_datos` | La tienda y sus datos fijos | No |

Las consultas de `tienda/ia/` y la descripción «con órdenes» de un producto están **escritas a mano** imitando
lo que puede hacer un modelo; no salen de un modelo concreto.

## Entregar

El repositorio de la pareja (sin `myvenv/` ni `db.sqlite3`), con commits de los dos, y el informe con las tablas y
capturas, **una sola vez por pareja**, como segunda entrega de laboratorio de la semana 7.

---

## Cómo ejecutar
Ver «Empezar» arriba. Resumen: `python -m venv myvenv`, `myvenv\Scripts\activate`,
`pip install -r requirements.txt -r requirements-dev.txt`, `python manage.py migrate`, `python manage.py cargar_datos`.

## Cómo probar
```powershell
python manage.py test                # las 19 pruebas
python manage.py duelo --detalle     # por parte, contra tienda/alumno/
ruff check . ; ruff format --check .
```

## Estructura de ramas
`main` (entrega) ← `develop` ← una rama por tarea: `chore/config-agentes`, `feature/parte1-consultas-orm`,
`feature/parte2-script-reporte`, `feature/parte3-mcp-config`, `feature/parte4-duelo-correccion`, `docs/informe`.
Detalles y convención de commits en [CONTRIBUTING.md](CONTRIBUTING.md).

## Trabajar con Claude Code / opencode / Codex
Las tres herramientas comparten las mismas reglas y roles:
- `AGENTS.md` es la fuente única (opencode y Codex lo leen directamente; `CLAUDE.md` solo importa `@AGENTS.md`).
- Los subagentes se definen una vez en `agents-src/<rol>.md` y `python scripts/dev/sync_agents.py` genera
  `.claude/agents/`, `.opencode/agents/` y `.codex/agents/`. No edites los generados; `--check` verifica que estén al día.
- Alcance: `read-only` y `scoped-write` se hacen cumplir con permisos de ruta en opencode; en Claude Code y Codex
  la restricción de rutas va en las instrucciones del rol (esas herramientas no la permiten por subagente).
