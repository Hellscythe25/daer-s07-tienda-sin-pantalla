"""PARTE 1 — Las seis consultas del ORM. Son la única «puerta» a los datos: las usan la CLI (Parte 2)
y el servidor MCP (Parte 3), así que lo que devuelvan aquí es lo que verá una persona, un script o un agente.

Reglas:
- Todo con el ORM: filter, exclude, Q, F, annotate, aggregate, select_related… Nada de recorrer tablas
  enteras en Python para filtrar o sumar, y nada de SQL a mano.
- Devuelvan datos simples (listas, diccionarios, números, Decimal): no QuerySets ni objetos del modelo.
- Los importes son Decimal: no los conviertan a float.

Comprueben su avance con: python manage.py duelo
Los datos son fijos (`python manage.py cargar_datos`), así que cada pregunta tiene una respuesta conocida.
"""

from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q, Sum  # noqa: F401  (los van a necesitar)

from tienda.models import Cliente, LineaPedido, Pedido, Producto  # noqa: F401


def productos_por_categoria(nombre):
    """Productos de la categoría `nombre`, ordenados por nombre.

    El nombre de la categoría NO distingue mayúsculas: «gaseosas» y «Gaseosas» dan lo mismo.
    Devuelve [{'nombre', 'precio', 'stock', 'descripcion'}, ...]; lista vacía si la categoría no existe.
    """
    raise NotImplementedError('TODO(alumno) Parte 1: productos_por_categoria en tienda/alumno/consultas.py')


def buscar_productos(texto):
    """Nombres de los productos cuyo nombre O descripción contienen `texto` (sin distinguir mayúsculas),
    ordenados. Pista: una condición O entre dos campos se escribe con objetos Q.
    """
    raise NotImplementedError('TODO(alumno) Parte 1: buscar_productos')


def stock_bajo(umbral=5):
    """Productos con stock menor o igual a `umbral`, del que menos tiene al que más (y por nombre si empatan).
    Devuelve [{'nombre', 'stock'}, ...].
    """
    raise NotImplementedError('TODO(alumno) Parte 1: stock_bajo')


def ventas_por_categoria():
    """Importe vendido por categoría, contando SOLO los pedidos pagados, de mayor a menor.

    El importe de una línea es cantidad × precio_unitario (el precio al momento de la venta, no el actual).
    Devuelve [{'categoria', 'total'}, ...] con `total` en Decimal.
    Pista: values() para agrupar, annotate(Sum(...)) para sumar y F() para multiplicar dos campos.
    """
    raise NotImplementedError('TODO(alumno) Parte 1: ventas_por_categoria')


def clientes_frecuentes(minimo=2):
    """Clientes con al menos `minimo` pedidos PAGADOS (los pendientes y anulados no cuentan), de más a menos
    pedidos y por nombre si empatan. Devuelve [{'nombre', 'pedidos_pagados'}, ...].
    Pista: Count admite un filter=Q(...).
    """
    raise NotImplementedError('TODO(alumno) Parte 1: clientes_frecuentes')


def detalle_pedido(pedido_id):
    """Detalle de un pedido, o None si no existe.

    Devuelve {'pedido', 'cliente' (nombre), 'estado', 'lineas': [{'producto', 'cantidad', 'precio_unitario',
    'subtotal'}], 'total'} con importes en Decimal.
    Tiene que resolverse en DOS consultas a la base de datos, tenga las líneas que tenga: una para el pedido
    con su cliente y otra para las líneas con su producto (select_related).
    """
    raise NotImplementedError('TODO(alumno) Parte 1: detalle_pedido')
