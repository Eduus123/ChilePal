from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.pedidos import (crear_pedido, obtener_pedidos_por_cliente,
                             obtener_pedidos_por_vendedor, obtener_pedidos_estado,
                             obtener_todos_los_pedidos, actualizar_estado_pedido,
                             obtener_pedido_por_id)
from models.productos import obtener_producto_por_id
from models.pagos import registrar_pago
from database.mysql_connection import query, query_one
from database.mongo_connection import log_accion
from routes.usuarios_routes import requiere_rol

pedidos_routes = Blueprint("pedidos_routes", __name__)


@pedidos_routes.route("/hacer_pedido", methods=["POST"])
@login_required
@requiere_rol("cliente")
def hacer_pedido():
    id_producto = int(request.form["id_producto"])
    id_sucursal = int(request.form["id_sucursal"])
    cantidad_kg = float(request.form["cantidad_kg"])
    observaciones = request.form.get("observaciones", "")

    if cantidad_kg <= 0:
        flash("La cantidad debe ser mayor a 0.")
        return redirect(url_for("productos_routes.catalogo"))

    producto = obtener_producto_por_id(id_producto)
    if not producto:
        flash("Producto no encontrado.")
        return redirect(url_for("productos_routes.catalogo"))

    stock = query_one(
        "SELECT cantidad_kg FROM stock WHERE id_producto = %s AND id_sucursal = %s",
        (id_producto, id_sucursal)
    )
    if not stock or stock["cantidad_kg"] < cantidad_kg:
        flash("Stock insuficiente.")
        return redirect(url_for("productos_routes.catalogo"))

    vendedor = query_one(
        "SELECT id_usuario FROM usuarios WHERE rol='vendedor' AND id_sucursal=%s AND activo=1 LIMIT 1",
        (id_sucursal,)
    )
    if not vendedor:
        flash("No hay vendedores disponibles.")
        return redirect(url_for("productos_routes.catalogo"))

    id_pedido = crear_pedido(
        id_cliente=current_user.db_id,
        id_vendedor=vendedor["id_usuario"],
        id_sucursal=id_sucursal,
        id_producto=id_producto,
        cantidad_kg=cantidad_kg,
        precio_unitario=float(producto["precio_kg"]),
        observaciones=observaciones
    )

    total = cantidad_kg * float(producto["precio_kg"])
    flash(f"Pedido #{id_pedido} realizado. Total: ${total:,.0f}")
    return redirect(url_for("pedidos_routes.mis_pedidos"))


@pedidos_routes.route("/mis_pedidos")
@login_required
@requiere_rol("cliente")
def mis_pedidos():
    pedidos = obtener_pedidos_por_cliente(current_user.db_id)
    return render_template("pedidos.html", pedidos=pedidos, vista="cliente")


@pedidos_routes.route("/empleado/dashboard")
@login_required
@requiere_rol("vendedor", "frigorifico", "repartidor")
def dashboard_empleado():
    rol = current_user.rol

    if rol == "vendedor":
        pedidos = obtener_pedidos_por_vendedor(current_user.db_id)
    elif rol == "frigorifico":
        pedidos = obtener_pedidos_estado("confirmado")
    else:
        pedidos = query("""
            SELECT p.id_pedido, p.estado, p.total,
                   u.nombre as cliente, su.ciudad as sucursal,
                   pr.nombre as producto, dp.cantidad_kg, d.id_despacho
            FROM despachos d
            JOIN pedidos p ON d.id_pedido = p.id_pedido
            JOIN usuarios u ON p.id_cliente = u.id_usuario
            JOIN sucursales su ON p.id_sucursal = su.id_sucursal
            LEFT JOIN detalle_pedido dp ON p.id_pedido = dp.id_pedido
            LEFT JOIN productos pr ON dp.id_producto = pr.id_producto
            WHERE d.id_repartidor = %s AND p.estado = 'despachado'
        """, (current_user.db_id,))

    return render_template("dashboard_empleado.html", pedidos=pedidos, rol=rol)


@pedidos_routes.route("/pedido/confirmar/<int:id_pedido>", methods=["POST"])
@login_required
@requiere_rol("vendedor")
def confirmar(id_pedido):
    actualizar_estado_pedido(id_pedido, "confirmado")
    log_accion(current_user.email, "vendedor", "confirmar_pedido", "pedidos",
               f"Pedido #{id_pedido} confirmado.")
    flash(f"Pedido #{id_pedido} confirmado.")
    return redirect(url_for("pedidos_routes.dashboard_empleado"))


@pedidos_routes.route("/pedido/cancelar/<int:id_pedido>", methods=["POST"])
@login_required
@requiere_rol("vendedor", "admin")
def cancelar(id_pedido):
    detalle = query_one("SELECT * FROM detalle_pedido WHERE id_pedido = %s", (id_pedido,))
    pedido = query_one("SELECT id_sucursal FROM pedidos WHERE id_pedido = %s", (id_pedido,))
    if detalle and pedido:
        query(
            "UPDATE stock SET cantidad_kg = cantidad_kg + %s WHERE id_producto = %s AND id_sucursal = %s",
            (detalle["cantidad_kg"], detalle["id_producto"], pedido["id_sucursal"]),
            fetch=False
        )
    actualizar_estado_pedido(id_pedido, "cancelado")
    log_accion(current_user.email, current_user.rol, "cancelar_pedido", "pedidos",
               f"Pedido #{id_pedido} cancelado.")
    flash(f"Pedido #{id_pedido} cancelado.")
    return redirect(url_for("pedidos_routes.dashboard_empleado"))


@pedidos_routes.route("/pedido/preparar/<int:id_pedido>", methods=["POST"])
@login_required
@requiere_rol("frigorifico")
def preparar(id_pedido):
    actualizar_estado_pedido(id_pedido, "en_preparacion")
    log_accion(current_user.email, "frigorifico", "preparar_pedido", "pedidos",
               f"Pedido #{id_pedido} preparado.")
    flash(f"Pedido #{id_pedido} preparado.")
    return redirect(url_for("pedidos_routes.dashboard_empleado"))


@pedidos_routes.route("/pedido/despachar/<int:id_pedido>", methods=["POST"])
@login_required
@requiere_rol("frigorifico")
def despachar(id_pedido):
    pedido = obtener_pedido_por_id(id_pedido)
    repartidor = query_one(
        "SELECT id_usuario FROM usuarios WHERE rol='repartidor' AND id_sucursal=%s AND activo=1 LIMIT 1",
        (pedido["id_sucursal"],)
    )
    if not repartidor:
        flash("No hay repartidores disponibles.")
        return redirect(url_for("pedidos_routes.dashboard_empleado"))

    query(
        "INSERT INTO despachos (id_pedido, id_repartidor, direccion_destino) VALUES (%s,%s,%s)",
        (id_pedido, repartidor["id_usuario"], "Por definir"),
        fetch=False
    )
    actualizar_estado_pedido(id_pedido, "despachado")
    log_accion(current_user.email, "frigorifico", "despachar_pedido", "despachos",
               f"Pedido #{id_pedido} despachado.")
    flash(f"Pedido #{id_pedido} despachado.")
    return redirect(url_for("pedidos_routes.dashboard_empleado"))


@pedidos_routes.route("/pedido/entregar/<int:id_pedido>", methods=["POST"])
@login_required
@requiere_rol("repartidor")
def entregar(id_pedido):
    metodo = request.form.get("metodo", "efectivo")
    pedido = query_one("SELECT total FROM pedidos WHERE id_pedido = %s", (id_pedido,))
    comprobante = registrar_pago(id_pedido, pedido["total"], metodo)
    actualizar_estado_pedido(id_pedido, "entregado")
    query("UPDATE despachos SET estado='entregado' WHERE id_pedido=%s", (id_pedido,), fetch=False)
    log_accion(current_user.email, "repartidor", "entregar_pedido", "pagos",
               f"Pedido #{id_pedido} entregado.")
    flash(f"Entrega registrada. Comprobante: {comprobante}")
    return redirect(url_for("pedidos_routes.dashboard_empleado"))


@pedidos_routes.route("/admin/pedidos")
@login_required
@requiere_rol("admin")
def admin_pedidos():
    pedidos = obtener_todos_los_pedidos()
    return render_template("pedidos.html", pedidos=pedidos, vista="admin")
