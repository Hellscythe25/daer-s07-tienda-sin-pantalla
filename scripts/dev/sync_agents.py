"""Genera los subagentes de cada herramienta desde `agents-src/` (fuente única).

    python scripts/dev/sync_agents.py          # escribe los archivos
    python scripts/dev/sync_agents.py --check  # falla (código 1) si lo generado no está al día

Salidas:
    .claude/agents/<rol>.md      Claude Code  (frontmatter name, description, tools)
    .opencode/agents/<rol>.md    opencode     (description, mode: subagent, permission)
    .codex/agents/<rol>.toml     Codex        (name, description, developer_instructions, sandbox_mode)

Formatos verificados en la documentación oficial (nov-2026) y con opencode 1.18.26 instalado.
Solo biblioteca estándar. `access`: read-only | scoped-write | full (+ `paths:` para scoped-write).
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
FUENTE = RAIZ / 'agents-src'
ACCESOS = ('read-only', 'scoped-write', 'full')
AVISO = 'GENERADO por scripts/dev/sync_agents.py desde agents-src/{rol}.md — no editar a mano.'
TRIPLE = "'" * 3
# Comandos de solo lectura / pruebas que un rol read-only puede ejecutar (opencode).
SHELL_SOLO_LECTURA = [
    'python manage.py test*',
    'python manage.py duelo*',
    'python manage.py tiendactl*',
    'myvenv/Scripts/python.exe manage.py test*',
    'myvenv/Scripts/python.exe manage.py duelo*',
    'myvenv/Scripts/python.exe manage.py tiendactl*',
    'myvenv\\Scripts\\python.exe manage.py test*',
    'myvenv\\Scripts\\python.exe manage.py duelo*',
    'myvenv\\Scripts\\python.exe manage.py tiendactl*',
    'git status*',
    'git diff*',
    'git log*',
    'git branch*',
    'ls*',
    'dir*',
    'cat *',
]


@dataclass
class Rol:
    name: str
    description: str
    access: str
    paths: list[str] = field(default_factory=list)
    cuerpo: str = ''


def leer_rol(ruta: Path) -> Rol:
    """Lee un `agents-src/<rol>.md` (frontmatter simple `clave: valor` y listas `- x`)."""
    texto = ruta.read_text(encoding='utf-8').replace('\r\n', '\n')
    if not texto.startswith('---\n'):
        raise ValueError(f'{ruta.name}: falta el frontmatter')
    cabecera, _, cuerpo = texto[4:].partition('\n---\n')
    datos: dict[str, object] = {}
    clave = ''
    for linea in cabecera.splitlines():
        if linea.startswith('  - ') and clave:
            lista = datos[clave]
            if isinstance(lista, list):
                lista.append(linea[4:].strip())
        elif ':' in linea:
            clave, _, valor = linea.partition(':')
            clave, valor = clave.strip(), valor.strip()
            datos[clave] = valor if valor else []
    paths = datos.get('paths')
    rol = Rol(
        str(datos.get('name', '')),
        str(datos.get('description', '')),
        str(datos.get('access', '')),
        list(paths) if isinstance(paths, list) else [],
        cuerpo.strip(),
    )
    if not (rol.name and rol.description) or rol.access not in ACCESOS:
        raise ValueError(f'{ruta.name}: name, description y access ({"|".join(ACCESOS)}) son obligatorios')
    if rol.access == 'scoped-write' and not rol.paths:
        raise ValueError(f'{ruta.name}: scoped-write necesita `paths`')
    return rol


def nota_alcance(rol: Rol, herramienta: str) -> str:
    """Párrafo que deja explícito el alcance, porque no todas las herramientas pueden forzarlo."""
    if rol.access == 'read-only':
        return (
            '## Alcance\nSOLO LECTURA: no edites ni crees archivos. Puedes leer, buscar y ejecutar pruebas '
            'y comandos de consulta (git status/diff/log, manage.py test/duelo/tiendactl).'
        )
    if rol.access == 'full':
        return '## Alcance\nAcceso completo (edición y shell), respetando las reglas de oro de AGENTS.md.'
    rutas = ', '.join(f'`{p}`' for p in rol.paths)
    forzado = {
        'opencode': 'opencode lo hace cumplir con permisos de edición por ruta.',
        'claude': 'Claude Code no restringe rutas en el subagente: cúmplelo tú de forma estricta.',
        'codex': 'Codex no restringe rutas por subagente: cúmplelo tú de forma estricta.',
    }[herramienta]
    return (
        f'## Alcance\nEscritura limitada: solo puedes crear o editar archivos dentro de {rutas}. Cualquier '
        f'otra ruta es de solo lectura para ti. {forzado} Respeta además las reglas de oro de AGENTS.md.'
    )


def cuerpo_completo(rol: Rol, herramienta: str) -> str:
    return f'{rol.cuerpo}\n\n{nota_alcance(rol, herramienta)}\nLee AGENTS.md para las reglas del proyecto.\n'


def generar_claude(rol: Rol) -> str:
    """Claude Code: `tools` es una lista separada por comas; no admite rutas, así que van en el texto."""
    base = ['Read', 'Grep', 'Glob', 'Bash']
    tools = base if rol.access == 'read-only' else base + ['Edit', 'Write']
    return (
        f'---\nname: {rol.name}\ndescription: {rol.description}\ntools: {", ".join(tools)}\n---\n'
        f'<!-- {AVISO.format(rol=rol.name)} -->\n\n{cuerpo_completo(rol, "claude")}'
    )


def generar_opencode(rol: Rol) -> str:
    """opencode: `permission` con reglas de edición por ruta y de shell por comando."""
    lineas = ['---', f'description: {rol.description}', 'mode: subagent', 'permission:']
    if rol.access == 'full':
        lineas += ['  edit: allow', '  bash: allow']
    elif rol.access == 'read-only':
        lineas += ['  edit: deny', '  bash:', '    "*": deny']
        lineas += [f'    {json.dumps(c)}: allow' for c in SHELL_SOLO_LECTURA]
    else:
        lineas += ['  edit:', '    "*": deny']
        lineas += [f'    {json.dumps(p + "**" if p.endswith("/") else p)}: allow' for p in rol.paths]
        lineas += ['  bash: allow']
    lineas += ['---', f'<!-- {AVISO.format(rol=rol.name)} -->', '', cuerpo_completo(rol, 'opencode')]
    return '\n'.join(lineas)


def generar_codex(rol: Rol) -> str:
    """Codex: TOML con `developer_instructions` en cadena literal multilínea."""
    sandbox = 'read-only' if rol.access == 'read-only' else 'workspace-write'
    instrucciones = cuerpo_completo(rol, 'codex')
    if TRIPLE in instrucciones:
        raise ValueError(f'{rol.name}: el cuerpo no puede contener tres comillas simples seguidas')
    return (
        f'# {AVISO.format(rol=rol.name)}\nname = {json.dumps(rol.name)}\n'
        f'description = {json.dumps(rol.description, ensure_ascii=False)}\n'
        f'sandbox_mode = "{sandbox}"\ndeveloper_instructions = {TRIPLE}\n{instrucciones}{TRIPLE}\n'
    )


SALIDAS = [
    ('.claude/agents', '.md', generar_claude),
    ('.opencode/agents', '.md', generar_opencode),
    ('.codex/agents', '.toml', generar_codex),
]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description='Genera subagentes desde agents-src/')
    ap.add_argument('--check', action='store_true', help='solo comprobar que lo generado está al día')
    args = ap.parse_args(argv)
    roles = [leer_rol(p) for p in sorted(FUENTE.glob('*.md'))]
    if not roles:
        print('No hay roles en agents-src/', file=sys.stderr)
        return 1
    desfasados = 0
    for carpeta, ext, generar in SALIDAS:
        for rol in roles:
            destino = RAIZ / carpeta / f'{rol.name}{ext}'
            contenido = generar(rol)
            # Tolera CRLF: con core.autocrlf Git puede cambiar los finales de línea al clonar.
            actual = destino.read_bytes().decode('utf-8').replace('\r\n', '\n') if destino.exists() else None
            if actual == contenido:
                continue
            desfasados += 1
            if args.check:
                print(f'desactualizado: {destino.relative_to(RAIZ)}')
            else:
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_bytes(contenido.encode('utf-8'))  # LF siempre, también en Windows
                print(f'escrito: {destino.relative_to(RAIZ)}')
    if args.check:
        return 1 if desfasados else 0
    print(f'{len(roles)} roles × {len(SALIDAS)} herramientas; {desfasados} archivos actualizados.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
