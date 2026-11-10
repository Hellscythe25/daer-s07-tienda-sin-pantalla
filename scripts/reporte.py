"""Reporte de la tienda consumiendo la CLI `tiendactl --json` (Parte 2).

Uso (desde la raíz del repo, sin preguntar nada y sin escribir en la BD ni en archivos):

    python scripts/reporte.py                      # ventas, stock bajo y clientes frecuentes
    python scripts/reporte.py --umbral 3 --minimo 1
    python scripts/reporte.py --pedido 1           # añade el detalle de un pedido
    python scripts/reporte.py --demo-errores       # muestra los códigos 2 y 3 de la CLI

Contrato de `tiendactl` que se respeta: con --json, stdout es solo JSON; código 0 = bien (lista vacía incluida),
2 = argumentos inválidos, 3 = no existe. Código de salida de este script: 0 bien, 2 argumentos inválidos,
3 no existe, 1 cualquier otro fallo (JSON inválido, código inesperado, no se pudo ejecutar).

Intérprete: la variable de entorno TIENDA_PYTHON o, si no existe, el mismo que ejecuta este script.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[1]
TIMEOUT_S = 60


class ErrorCLI(Exception):
    """La CLI terminó con un código distinto de 0 (o dejó una salida que no es JSON)."""

    def __init__(self, codigo: int, mensaje: str) -> None:
        super().__init__(mensaje)
        self.codigo = codigo
        self.mensaje = mensaje


def ejecutar(*args: str) -> Any:
    """Ejecuta `tiendactl <args> --json` y devuelve el JSON ya parseado (importes como Decimal).

    Lanza ErrorCLI con el código de salida real: 2 = argumentos inválidos, 3 = no existe, 1 = otro fallo.
    """
    python = os.environ.get('TIENDA_PYTHON', sys.executable)
    orden = [python, 'manage.py', 'tiendactl', *args, '--json']
    try:
        r = subprocess.run(
            orden,
            cwd=RAIZ,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env={**os.environ, 'PYTHONUTF8': '1', 'PYTHONIOENCODING': 'utf-8'},  # tildes igual en Windows
            stdin=subprocess.DEVNULL,  # nunca esperar entrada del teclado
            timeout=TIMEOUT_S,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        raise ErrorCLI(1, f'no se pudo ejecutar tiendactl: {e}') from e
    if r.returncode == 0:
        try:
            # parse_float=Decimal: los importes no pasan nunca por float
            return json.loads(r.stdout, parse_float=Decimal)
        except json.JSONDecodeError as e:
            raise ErrorCLI(1, f'la salida de tiendactl no es JSON válido: {e}') from e
    detalle = (r.stderr or r.stdout).strip().splitlines()
    mensaje = detalle[-1] if detalle else 'sin mensaje'
    if r.returncode in (2, 3):
        raise ErrorCLI(r.returncode, mensaje)
    raise ErrorCLI(1, f'código de salida inesperado {r.returncode}: {mensaje}')


def tabla(titulo: str, filas: list[list[str]], cabecera: list[str]) -> str:
    """Tabla de texto con columnas alineadas; «(sin resultados)» si no hay filas."""
    if not filas:
        return f'{titulo}\n  (sin resultados)\n'
    todas = [cabecera, *filas]
    anchos = [max(len(f[i]) for f in todas) for i in range(len(cabecera))]
    lineas = ['  ' + '  '.join(c.ljust(anchos[i]) for i, c in enumerate(f)).rstrip() for f in todas]
    lineas.insert(1, '  ' + '  '.join('-' * a for a in anchos))
    return f'{titulo}\n' + '\n'.join(lineas) + '\n'


def soles(valor: Decimal) -> str:
    return f'S/ {valor:.2f}'


def reporte(umbral: int, minimo: int, pedido: int | None) -> str:
    """Arma el reporte completo; propaga ErrorCLI si alguna orden falla."""
    ventas = ejecutar('ventas')
    stock = ejecutar('stock', '--umbral', str(umbral))
    clientes = ejecutar('clientes', '--minimo', str(minimo))
    total = sum((Decimal(v['total']) for v in ventas), Decimal('0'))
    partes = [
        tabla(
            'Ventas pagadas por categoría',
            [[v['categoria'], soles(Decimal(v['total']))] for v in ventas],
            ['Categoría', 'Total'],
        ),
        f'  Total vendido: {soles(total)}\n',
        tabla(f'Stock bajo (<= {umbral})', [[s['nombre'], str(s['stock'])] for s in stock], ['Producto', 'Stock']),
        tabla(
            f'Clientes con al menos {minimo} pedidos pagados',
            [[c['nombre'], str(c['pedidos_pagados'])] for c in clientes],
            ['Cliente', 'Pagados'],
        ),
    ]
    if pedido is not None:
        d = ejecutar('pedido', str(pedido))
        filas = [[li['producto'], str(li['cantidad']), soles(Decimal(li['subtotal']))] for li in d['lineas']]
        partes.append(
            tabla(f'Pedido {d["pedido"]} de {d["cliente"]} ({d["estado"]})', filas, ['Producto', 'Cant.', 'Subtotal'])
        )
        partes.append(f'  Total: {soles(Decimal(d["total"]))}\n')
    return '\n'.join(partes)


def demo_errores() -> int:
    """Provoca a propósito un error 2 y un error 3 para mostrar cómo se manejan."""
    for descripcion, args in (('argumentos inválidos', ('stock', '--umbral', '-1')), ('no existe', ('pedido', '999'))):
        try:
            ejecutar(*args)
            print(f'{descripcion}: ¡no falló!', file=sys.stderr)
            return 1
        except ErrorCLI as e:
            print(f'tiendactl {" ".join(args)} -> código {e.codigo} ({descripcion}): {e.mensaje}')
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description='Reporte de la tienda vía tiendactl --json')
    ap.add_argument('--umbral', type=int, default=5, help='stock bajo: umbral (por defecto 5)')
    ap.add_argument('--minimo', type=int, default=2, help='clientes frecuentes: pedidos pagados mínimos')
    ap.add_argument('--pedido', type=int, help='incluye el detalle de este pedido')
    ap.add_argument('--demo-errores', action='store_true', help='muestra los códigos de salida 2 y 3')
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if args.demo_errores:
        return demo_errores()
    try:
        print(reporte(args.umbral, args.minimo, args.pedido))
    except ErrorCLI as e:
        print(f'error ({e.codigo}): {e.mensaje}', file=sys.stderr)
        return e.codigo
    return 0


if __name__ == '__main__':
    sys.exit(main())
