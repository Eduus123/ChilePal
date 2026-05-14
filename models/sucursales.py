from database.mysql_connection import query, query_one


def obtener_sucursales():
    return query("SELECT * FROM sucursales WHERE activa = 1")


def obtener_sucursal_por_id(id_sucursal):
    return query_one("SELECT * FROM sucursales WHERE id_sucursal = %s", (id_sucursal,))


def crear_sucursal(ciudad, direccion, telefono):
    return query(
        "INSERT INTO sucursales (ciudad, direccion, telefono) VALUES (%s, %s, %s)",
        (ciudad, direccion, telefono),
        fetch=False
    )
