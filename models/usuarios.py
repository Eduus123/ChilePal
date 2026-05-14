import bcrypt
from database.mysql_connection import query, query_one


def crear_usuario(nombre, email, password, rol, id_sucursal=None):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    return query(
        "INSERT INTO usuarios (nombre, email, password, rol, id_sucursal) VALUES (%s, %s, %s, %s, %s)",
        (nombre, email, hashed, rol, id_sucursal),
        fetch=False
    )


def obtener_usuario_por_email(email):
    return query_one(
        "SELECT * FROM usuarios WHERE email = %s AND activo = 1",
        (email,)
    )


def obtener_usuario_por_id(id_usuario):
    return query_one(
        "SELECT * FROM usuarios WHERE id_usuario = %s AND activo = 1",
        (id_usuario,)
    )


def verificar_password(password_plana, password_hash):
    return bcrypt.checkpw(password_plana.encode(), password_hash.encode())


def obtener_usuarios():
    return query("""
        SELECT u.*, s.ciudad AS sucursal
        FROM usuarios u
        LEFT JOIN sucursales s ON u.id_sucursal = s.id_sucursal
        ORDER BY u.rol, u.nombre
    """)


def desactivar_usuario(id_usuario):
    query(
        "UPDATE usuarios SET activo = 0 WHERE id_usuario = %s",
        (id_usuario,),
        fetch=False
    )
