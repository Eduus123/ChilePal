from database.mysql_connection import query, query_one
from database.mongo_connection import registrar_contacto


def crear_pedido(id_cliente, id_vendedor, id_sucursal, id_producto,
                 cantidad_kg, precio_unitario, observaciones=""):
    total = cantidad_kg * precio_unitario

    id_pedido = query(
        "INSERT INTO pedidos (id_cliente, id_vendedor, id_sucursal, total, observaciones) VALUES (%s, %s, %s, %s, %s)",
        (id_cliente, id_vendedor, id_sucursal, total, observaciones),
        fetch=False
    )

    query(
        "INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad_kg, precio_unitario) VALUES (%s, %s, %s, %s)",
        (id_pedido, id_producto, cantidad_kg, precio_unitario),
        fetch=False
    )

    query(
        "UPDATE stock SET cantidad_kg = cantidad_kg - %s WHERE id_producto = %s AND id_sucursal = %s",
        (cantidad_kg, id_producto, id_sucursal),
        fetch=False
    )

    registrar_contacto(
        id_pedido=id_pedido,
        id_cliente=id_cliente,
        id_vendedor=id_vendedor,
        canal="web",
        notas=f"Pedido {cantidad_kg}kg vía web. {observaciones}",
        resultado="pedido_registrado"
    )

    return id_pedido


def obtener_pedidos_por_cliente(id_cliente):
    return query("""
        SELECT p.id_pedido, p.fecha_pedido, p.estado, p.total,
               su.ciudad AS sucursal, pr.nombre AS producto, dp.cantidad_kg
        FROM pedidos p
        JOIN sucursales su ON p.id_sucursal = su.id_sucursal
        LEFT JOIN detalle_pedido dp ON p.id_pedido = dp.id_pedido
        LEFT JOIN productos pr ON dp.id_producto = pr.id_producto
        WHERE p.id_cliente = %s
        ORDER BY p.fecha_pedido DESC
    """, (id_cliente,))


def obtener_pedidos_por_vendedor(id_vendedor):
    return query("""
        SELECT p.id_pedido, p.fecha_pedido, p.estado, p.total,
               u.nombre AS cliente, u.email AS email_cliente,
               su.ciudad AS sucursal, pr.nombre AS producto, dp.cantidad_kg
        FROM pedidos p
        JOIN usuarios u ON p.id_cliente = u.id_usuario
        JOIN sucursales su ON p.id_sucursal = su.id_sucursal
        LEFT JOIN detalle_pedido dp ON p.id_pedido = dp.id_pedido
        LEFT JOIN productos pr ON dp.id_producto = pr.id_producto
        WHERE p.id_vendedor = %s
        ORDER BY p.fecha_pedido DESC LIMIT 40
    """, (id_vendedor,))


def obtener_pedidos_estado(estado):
    return query("""
        SELECT p.id_pedido, p.fecha_pedido, p.estado, p.total,
               u.nombre AS cliente, su.ciudad AS sucursal,
               pr.nombre AS producto, dp.cantidad_kg
        FROM pedidos p
        JOIN usuarios u ON p.id_cliente = u.id_usuario
        JOIN sucursales su ON p.id_sucursal = su.id_sucursal
        LEFT JOIN detalle_pedido dp ON p.id_pedido = dp.id_pedido
        LEFT JOIN productos pr ON dp.id_producto = pr.id_producto
        WHERE p.estado = %s
        ORDER BY p.fecha_pedido ASC
    """, (estado,))


def obtener_todos_los_pedidos():
    return query("""
        SELECT p.id_pedido, p.fecha_pedido, p.estado, p.total,
               u.nombre AS cliente, e.nombre AS vendedor,
               su.ciudad AS sucursal, pr.nombre AS producto, dp.cantidad_kg
        FROM pedidos p
        JOIN usuarios u ON p.id_cliente = u.id_usuario
        JOIN usuarios e ON p.id_vendedor = e.id_usuario
        JOIN sucursales su ON p.id_sucursal = su.id_sucursal
        LEFT JOIN detalle_pedido dp ON p.id_pedido = dp.id_pedido
        LEFT JOIN productos pr ON dp.id_producto = pr.id_producto
        ORDER BY p.fecha_pedido DESC
    """)


def actualizar_estado_pedido(id_pedido, nuevo_estado):
    query(
        "UPDATE pedidos SET estado = %s WHERE id_pedido = %s",
        (nuevo_estado, id_pedido),
        fetch=False
    )


def obtener_pedido_por_id(id_pedido):
    return query_one("""
        SELECT p.*, u.nombre AS cliente, su.ciudad AS sucursal
        FROM pedidos p
        JOIN usuarios u ON p.id_cliente = u.id_usuario
        JOIN sucursales su ON p.id_sucursal = su.id_sucursal
        WHERE p.id_pedido = %s
    """, (id_pedido,))
