from flask import Flask, redirect, render_template
from flask_login import LoginManager
from config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "usuarios_routes.login"

from routes.usuarios_routes import usuarios_routes, Usuario
from routes.productos_routes import productos_routes
from routes.pedidos_routes import pedidos_routes
from routes.sucursales_routes import sucursales_routes

app.register_blueprint(usuarios_routes)
app.register_blueprint(productos_routes)
app.register_blueprint(pedidos_routes)
app.register_blueprint(sucursales_routes)

from models.usuarios import obtener_usuario_por_id

@login_manager.user_loader
def load_user(user_id):
    usuario = obtener_usuario_por_id(int(user_id))
    if usuario:
        return Usuario(usuario["id_usuario"], usuario["nombre"],
                       usuario["email"], usuario["rol"])
    return None


@app.route("/")
def inicio():
    return render_template("index.html")


with app.app_context():
    from database.mysql_connection import inicializar_mysql
    from database.mongo_connection import inicializar_mongodb
    inicializar_mysql()
    inicializar_mongodb()

    try:
        from models.usuarios import crear_usuario, obtener_usuario_por_email
        if not obtener_usuario_por_email("admin@chilepal.cl"):
            crear_usuario(nombre="Administrador", email="admin@chilepal.cl",
                          password="admin123", rol="admin", id_sucursal=1)
            print("✔ Admin creado: admin@chilepal.cl / admin123")
    except Exception as e:
        print(f"⚠ Error creando admin: {e}")


if __name__ == "__main__":
    print("✔ Iniciando servidor Flask...")
    app.run(debug=False, host="127.0.0.1", port=5000)
