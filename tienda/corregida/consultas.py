"""Copia corregida de tienda/ia/consultas.py (Parte 4 del laboratorio).

Cuatro correcciones sobre la versión de la IA, marcadas con «CORRECCIÓN n»:
1 productos_por_categoria, 2 buscar_productos, 3 ventas_por_categoria, 4 detalle_pedido.
"""

from decimal import Decimal

from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q, Sum

from tienda.models import Cliente, LineaPedido, Pedido, Producto


def productos_por_categoria(nombre):
    # CORRECCIÓN 1: iexact, para no distinguir mayúsculas
    productos = Producto.objects.filter(categoria__nombre__iexact=nombre).order_by('nombre')
    return [{'nombre': p.nombre, 'precio': p.precio, 'stock': p.stock, 'descripcion': p.descripcion} for p in productos]


def buscar_productos(texto):
    # CORRECCIÓN 2: condición O (Q | Q), no Y
    productos = Producto.objects.filter(Q(nombre__icontains=texto) | Q(descripcion__icontains=texto))
    return [p.nombre for p in productos.order_by('nombre')]


def stock_bajo(umbral=5):
    productos = Producto.objects.filter(stock__lte=umbral).order_by('stock', 'nombre')
    return [{'nombre': p.nombre, 'stock': p.stock} for p in productos]


def ventas_por_categoria():
    importe = ExpressionWrapper(
        F('cantidad') * F('precio_unitario'), output_field=DecimalField(max_digits=10, decimal_places=2)
    )
    filas = (
        LineaPedido.objects.filter(pedido__estado=Pedido.PAGADO)  # CORRECCIÓN 3: solo pedidos pagados
        .values('producto__categoria__nombre')
        .annotate(total=Sum(importe))
        .order_by('-total', 'producto__categoria__nombre')
    )
    return [{'categoria': f['producto__categoria__nombre'], 'total': f['total']} for f in filas]


def clientes_frecuentes(minimo=2):
    clientes = (
        Cliente.objects.annotate(pedidos_pagados=Count('pedidos', filter=Q(pedidos__estado=Pedido.PAGADO)))
        .filter(pedidos_pagados__gte=minimo)
        .order_by('-pedidos_pagados', 'nombre')
    )
    return [{'nombre': c.nombre, 'pedidos_pagados': c.pedidos_pagados} for c in clientes]


def detalle_pedido(pedido_id):
    pedido = Pedido.objects.select_related('cliente').filter(pk=pedido_id).first()  # CORRECCIÓN 4: cliente en el JOIN
    if pedido is None:
        return None
    lineas = [
        {
            'producto': linea.producto.nombre,
            'cantidad': linea.cantidad,
            'precio_unitario': linea.precio_unitario,
            'subtotal': linea.cantidad * linea.precio_unitario,
        }
        for linea in pedido.lineas.select_related('producto')
    ]  # CORRECCIÓN 4: producto en el JOIN
    return {
        'pedido': pedido.pk,
        'cliente': pedido.cliente.nombre,
        'estado': pedido.estado,
        'lineas': lineas,
        'total': sum((linea['subtotal'] for linea in lineas), Decimal('0')),
    }
