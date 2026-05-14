from database.mysql_connection import query, query_one


def obtener_productos(id_sucursal=None):
    if id_sucursal:
        return query("""
            SELECT p.id_producto, p.nombre, p.variedad, p.calibre,
                   p.precio_kg, p.es_temporada,
                   s.id_sucursal, s.cantidad_kg, su.ciudad
            FROM productos p
            JOIN stock s ON p.id_producto = s.id_producto
            JOIN sucursales su ON s.id_sucursal = su.id_sucursal
            WHERE p.activo = 1 AND s.cantidad_kg > 0 AND s.id_sucursal = %s
            ORDER BY p.es_temporada ASC, p.variedad, p.calibre
        """, (id_sucursal,))
    return query("""
        SELECT p.id_producto, p.nombre, p.variedad, p.calibre,
               p.precio_kg, p.es_temporada,
               s.id_sucursal, s.cantidad_kg, su.ciudad
        FROM productos p
        JOIN stock s ON p.id_producto = s.id_producto
        JOIN sucursales su ON s.id_sucursal = su.id_sucursal
        WHERE p.activo = 1 AND s.cantidad_kg > 0
        ORDER BY p.es_temporada ASC, p.variedad, p.calibre
    """)


def obtener_producto_por_id(id_producto):
    return query_one(
        "SELECT * FROM productos WHERE id_producto = %s AND activo = 1",
        (id_producto,)
    )


def crear_producto(nombre, variedad, calibre, precio_kg, es_temporada,
                   id_sucursal_inicial=None, stock_inicial=0):
    id_prod = query(
        "INSERT INTO productos (nombre, variedad, calibre, precio_kg, es_temporada) VALUES (%s, %s, %s, %s, %s)",
        (nombre, variedad, calibre or None, precio_kg, es_temporada),
        fetch=False
    )
    sucursales = query("SELECT id_sucursal FROM sucursales WHERE activa = 1")
    for s in sucursales:
        # Si esta es la sucursal seleccionada, usar el stock inicial ingresado
        cantidad = stock_inicial if str(s["id_sucursal"]) == str(id_sucursal_inicial) else 0
        query(
            "INSERT IGNORE INTO stock (id_producto, id_sucursal, cantidad_kg) VALUES (%s, %s, %s)",
            (id_prod, s["id_sucursal"], cantidad),
            fetch=False
        )
    return id_prod


def actualizar_stock(id_producto, id_sucursal, cantidad_kg):
    query(
        "UPDATE stock SET cantidad_kg = %s WHERE id_producto = %s AND id_sucursal = %s",
        (cantidad_kg, id_producto, id_sucursal),
        fetch=False
    )


def obtener_todo_el_stock():
    return query("""
        SELECT p.nombre, p.variedad, p.calibre, p.precio_kg,
               s.cantidad_kg, su.ciudad, s.id_producto, s.id_sucursal
        FROM stock s
        JOIN productos p ON s.id_producto = p.id_producto
        JOIN sucursales su ON s.id_sucursal = su.id_sucursal
        WHERE p.activo = 1
        ORDER BY su.ciudad, p.variedad
    """)