from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.productos import (obtener_productos, crear_producto,
                               actualizar_stock, obtener_todo_el_stock)
from models.sucursales import obtener_sucursales
from database.mongo_connection import log_accion
from routes.usuarios_routes import requiere_rol

productos_routes = Blueprint("productos_routes", __name__)


@productos_routes.route("/catalogo")
def catalogo():
    sucursales = obtener_sucursales()
    # Leer el filtro de sucursal desde query param (?sucursal=1)
    id_sucursal = request.args.get("sucursal", type=int)
    productos = obtener_productos(id_sucursal=id_sucursal)
    return render_template("productos.html", productos=productos,
                           sucursales=sucursales, id_sucursal_activa=id_sucursal)


@productos_routes.route("/admin/productos")
@login_required
@requiere_rol("admin")
def admin_productos():
    productos = obtener_productos()
    stock = obtener_todo_el_stock()
    sucursales = obtener_sucursales()
    return render_template("admin_productos.html", productos=productos,
                           stock=stock, sucursales=sucursales)


@productos_routes.route("/admin/agregar_producto", methods=["POST"])
@login_required
@requiere_rol("admin")
def agregar_producto():
    d = request.form
    crear_producto(
        nombre=d["nombre"],
        variedad=d["variedad"],
        calibre=d.get("calibre") or None,
        precio_kg=float(d["precio_kg"]),
        es_temporada=(d.get("es_temporada") == "1"),
        id_sucursal_inicial=d.get("id_sucursal_inicial"),
        stock_inicial=float(d.get("stock_inicial") or 0)
    )
    log_accion(current_user.email, "admin", "agregar_producto", "productos",
               f"Producto agregado: {d['nombre']}")
    flash(f"Producto {d['nombre']} agregado.")
    return redirect(url_for("productos_routes.admin_productos"))


@productos_routes.route("/admin/actualizar_stock", methods=["POST"])
@login_required
@requiere_rol("admin")
def update_stock():
    actualizar_stock(
        id_producto=request.form["id_producto"],
        id_sucursal=request.form["id_sucursal"],
        cantidad_kg=request.form["cantidad_kg"]
    )
    log_accion(current_user.email, "admin", "actualizar_stock", "stock",
               f"Stock actualizado: prod {request.form['id_producto']}")
    flash("Stock actualizado.")
    return redirect(url_for("productos_routes.admin_productos"))