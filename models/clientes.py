from models.usuarios import crear_usuario, obtener_usuario_por_email


def registrar_cliente(nombre, email, password, telefono, ciudad, direccion):
    if obtener_usuario_por_email(email):
        return False
    crear_usuario(nombre=nombre, email=email, password=password, rol="cliente", id_sucursal=None)
    return True
