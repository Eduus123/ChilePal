from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.sucursales import obtener_sucursales, crear_sucursal
from database.mongo_connection import log_accion
from routes.usuarios_routes import requiere_rol

sucursales_routes = Blueprint("sucursales_routes", __name__)


@sucursales_routes.route("/admin/sucursales")
@login_required
@requiere_rol("admin")
def listar():
    sucursales = obtener_sucursales()
    return render_template("sucursales.html", sucursales=sucursales)


@sucursales_routes.route("/admin/agregar_sucursal", methods=["POST"])
@login_required
@requiere_rol("admin")
def agregar():
    d = request.form
    crear_sucursal(d["ciudad"], d["direccion"], d.get("telefono", ""))
    log_accion(current_user.email, "admin", "agregar_sucursal", "sucursales",
               f"Nueva sucursal: {d['ciudad']}")
    flash(f"Sucursal en {d['ciudad']} agregada.")
    return redirect(url_for("sucursales_routes.listar"))
