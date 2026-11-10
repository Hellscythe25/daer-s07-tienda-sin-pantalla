# Parte 4 — El duelo: las consultas de la IA

Comandos ejecutados (resultados reales, `develop` con las Partes 1-3 integradas):

| Comando | Resultado |
|---|---|
| `python manage.py duelo` | 19 de 19 en verde (consultas propias) |
| `python manage.py duelo ia` | **4 en rojo de 19** (todas en la Parte 1; CLI 6/6 y MCP 5/5 en verde) |
| `python manage.py duelo --iniciar-corregida` | copia `tienda/ia/` → `tienda/corregida/` |
| `python manage.py duelo corregida` (antes de corregir) | 4 en rojo de 19 |
| `python manage.py duelo corregida` (después) | **19 de 19 en verde** |

## Los cuatro fallos

| # | Función | Prueba que lo detecta | Tipo de error | Causa | Corrección |
|---|---|---|---|---|---|
| 1 | `productos_por_categoria` | `test_productos_por_categoria` | Lógico (semántica de datos) | `categoria__nombre=nombre` distingue mayúsculas en SQLite: «gaseosas» devuelve `[]` | `categoria__nombre__iexact=nombre` |
| 2 | `buscar_productos` | `test_buscar_productos_en_nombre_o_descripcion` | Lógico (operador) | `filter(nombre__icontains=…, descripcion__icontains=…)` combina con **Y**: el texto tendría que estar en ambos campos; devuelve `[]` | `Q(nombre__icontains=…) \| Q(descripcion__icontains=…)` |
| 3 | `ventas_por_categoria` | `test_ventas_por_categoria_solo_pagadas` | Lógico (regla de negocio omitida) | No filtra por estado: suma pedidos pendientes y anulados (Chocolates 23.40 en vez de 8.40) | `.filter(pedido__estado=Pedido.PAGADO)` antes del `values/annotate` |
| 4 | `detalle_pedido` | `test_detalle_de_un_pedido_en_dos_consultas` | Rendimiento (N+1) | Sin `select_related`: 5 consultas para un pedido de 2 líneas (1 pedido + 1 líneas + 1 producto por línea + 1 cliente); crece con las líneas | `select_related('cliente')` en el pedido y `select_related('producto')` en las líneas → 2 consultas |

Salida real del fallo 4: `AssertionError: 5 != 2 : 5 queries executed, 2 expected`.
Salida real del fallo 3: `Decimal('23.4000000000000') != Decimal('8.40')` para Chocolates.

## Observaciones extra (no las detectan las pruebas)
- Tipo de la suma: la IA usa `sum(..., 0)`; con un pedido sin líneas el total sería el entero `0`, no un `Decimal`. Se
  cambió a `Decimal('0')` en la copia corregida.
- En `ventas_por_categoria` se añadió desempate por nombre de categoría para un orden determinista.
- La IA acertó 4 de 8 consultas de la Parte 1 (stock_bajo y clientes_frecuentes pasan): los errores están en
  detalles que un enunciado en lenguaje natural no hace evidentes (mayúsculas, Y/O, estado, N+1).

## Para la defensa oral
Por qué las pruebas son el oráculo: los fallos 1-3 devuelven datos plausibles pero incorrectos sin lanzar error, y
el 4 devuelve datos correctos pero con coste creciente; solo una prueba con datos fijos (y `assertNumQueries`) los
detecta.

[CAPTURA: `python manage.py duelo ia --detalle` con los 4 fallos]
[CAPTURA: `python manage.py duelo corregida` con 19 de 19 en verde]
