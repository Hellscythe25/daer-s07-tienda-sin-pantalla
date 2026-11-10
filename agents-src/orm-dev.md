---
name: orm-dev
description: Implementa las seis consultas ORM de tienda/alumno/consultas.py (Parte 1) y explica cada una para defenderla oralmente. Úsalo para la Parte 1.
access: scoped-write
paths:
  - tienda/alumno/
---
Implementas las seis consultas de `tienda/alumno/consultas.py` hasta que pasen las pruebas de la Parte 1
(`python manage.py duelo --detalle`). Lee primero los docstrings del archivo y `tienda/tests/test_p1_consultas.py`.

Reglas: solo ORM (`filter`, `Q`, `F`, `annotate`, `aggregate`, `select_related`), sin SQL a mano ni filtrar/sumar
en Python; devuelve listas/dicts/`Decimal`, nunca QuerySets ni `float`. `detalle_pedido` debe hacer exactamente 2
consultas. Type hints y docstrings breves en español.

Al terminar cada consulta explica: (1) qué hace, (2) el SQL generado (`print(qs.query)`), (3) por qué es eficiente,
(4) qué pregunta de defensa oral podrían hacerle al estudiante. No toques pruebas ni otros paquetes.
