from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import UserMixin, login_user, logout_user, login_required, current_user
from models.usuarios import (obtener_usuario_por_email, crear_usuario,
                              obtener_usuarios, verificar_password, desactivar_usuario)
from models.sucursales import obtener_sucursales
from database.mongo_connection import log_accion, obtener_logs_recientes


class Usuario(UserMixin):
    def __init__(self, id_usuario, nombre, email, rol):
        self.id = str(id_usuario)
        self.db_id = id_usuario
        self.nombre = nombre
        self.email = email
        self.rol = rol


usuarios_routes = Blueprint("usuarios_routes", __name__)


def requiere_rol(*roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("usuarios_routes.login"))
            if current_user.rol not in roles:
                flash("No tienes permisos para acceder a esa sección.")
                return redirect(url_for("usuarios_routes.login"))
            return func(*args, **kwargs)
        return wrapper
    return decorator


@usuarios_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        usuario = obtener_usuario_por_email(email)

        if usuario and verificar_password(password, usuario["password"]):
            user = Usuario(usuario["id_usuario"], usuario["nombre"],
                           usuario["email"], usuario["rol"])
            login_user(user)
            log_accion(usuario["email"], usuario["rol"], "login", "usuarios", "Inicio de sesión.")
            flash(f"Bienvenido {usuario['nombre']}.")

            if usuario["rol"] == "cliente":
                return redirect(url_for("productos_routes.catalogo"))
            elif usuario["rol"] == "admin":
                return redirect(url_for("usuarios_routes.dashboard_admin"))
            else:
                return redirect(url_for("pedidos_routes.dashboard_empleado"))

        flash("Correo o contraseña incorrectos.")

    return render_template("login.html")


@usuarios_routes.route("/logout")
@login_required
def logout():
    log_accion(current_user.email, current_user.rol, "logout", "usuarios", "Cierre de sesión.")
    logout_user()
    flash("Sesión cerrada.")
    return redirect(url_for("usuarios_routes.login"))


@usuarios_routes.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        d = request.form
        if obtener_usuario_por_email(d["email"]):
            flash("El correo ya existe.")
            return redirect(url_for("usuarios_routes.registro"))
        crear_usuario(nombre=d["nombre"], email=d["email"],
                      password=d["password"], rol="cliente", id_sucursal=None)
        flash("Cuenta creada correctamente.")
        return redirect(url_for("usuarios_routes.login"))
    return render_template("registro.html")


@usuarios_routes.route("/admin/dashboard")
@login_required
@requiere_rol("admin")
def dashboard_admin():
    from database.mysql_connection import query
    from models.pagos import obtener_total_ventas
    stats = {
        "total_pedidos":     query("SELECT COUNT(*) as n FROM pedidos")[0]["n"],
        "pedidos_pendientes":query("SELECT COUNT(*) as n FROM pedidos WHERE estado='pendiente'")[0]["n"],
        "total_clientes":    query("SELECT COUNT(*) as n FROM usuarios WHERE rol='cliente' AND activo=1")[0]["n"],
        "total_empleados":   query("SELECT COUNT(*) as n FROM usuarios WHERE rol != 'cliente' AND activo=1")[0]["n"],
        "ventas_totales":    obtener_total_ventas(),
    }
    logs = obtener_logs_recientes(20)
    return render_template("dashboard.html", stats=stats, logs=logs)


@usuarios_routes.route("/admin/empleados")
@login_required
@requiere_rol("admin")
def empleados():
    usuarios = obtener_usuarios()
    sucursales = obtener_sucursales()
    return render_template("empleados.html", empleados=usuarios, sucursales=sucursales)


@usuarios_routes.route("/admin/agregar_empleado", methods=["POST"])
@login_required
@requiere_rol("admin")
def agregar_empleado():
    d = request.form
    crear_usuario(nombre=d["nombre"], email=d["email"],
                  password=d["password"], rol=d["rol"], id_sucursal=d["id_sucursal"])
    log_accion(current_user.email, "admin", "crear_empleado", "usuarios",
               f"Empleado creado: {d['email']}")
    flash(f"Empleado {d['nombre']} creado.")
    return redirect(url_for("usuarios_routes.empleados"))


@usuarios_routes.route("/admin/desactivar_empleado/<int:id_usuario>", methods=["POST"])
@login_required
@requiere_rol("admin")
def desactivar(id_usuario):
    desactivar_usuario(id_usuario)
    log_accion(current_user.email, "admin", "desactivar_usuario", "usuarios",
               f"Usuario #{id_usuario} desactivado.")
    flash("Usuario desactivado.")
    return redirect(url_for("usuarios_routes.empleados"))
