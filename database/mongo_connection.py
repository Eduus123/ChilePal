from pymongo import MongoClient
from datetime import datetime
from config import MONGO_URI, MONGO_DATABASE

_client = None


def get_mongo_db():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client[MONGO_DATABASE]


def inicializar_mongodb():
    try:
        db = get_mongo_db()
        existentes = db.list_collection_names()

        if "historial_contactos" not in existentes:
            db.create_collection("historial_contactos")
            db.historial_contactos.create_index([("id_pedido_ref", 1)])

        if "logs_sistema" not in existentes:
            db.create_collection("logs_sistema")
            db.logs_sistema.create_index([("timestamp", -1)])

        if "catalogo_extendido" not in existentes:
            db.create_collection("catalogo_extendido")
            db.catalogo_extendido.insert_many([
                {
                    "nombre": "Palta Hass Extra",
                    "descripcion": "Mayor tamaño y calidad.",
                    "temporada": "Todo el año"
                },
                {
                    "nombre": "Mango Kent",
                    "descripcion": "Producto estacional.",
                    "temporada": "Verano"
                }
            ])

        print("✔ MongoDB inicializado.")

    except Exception as e:
        print(f"✖ Error MongoDB: {e}")


def log_accion(usuario, rol, accion, entidad, detalle, ip="127.0.0.1"):
    db = get_mongo_db()
    db.logs_sistema.insert_one({
        "timestamp": datetime.now(),
        "usuario": usuario,
        "rol": rol,
        "accion": accion,
        "entidad": entidad,
        "detalle": detalle,
        "ip": ip
    })


def registrar_contacto(id_pedido, id_cliente, id_vendedor, canal, notas, resultado):
    db = get_mongo_db()
    db.historial_contactos.insert_one({
        "id_pedido_ref": id_pedido,
        "id_cliente_ref": id_cliente,
        "id_vendedor_ref": id_vendedor,
        "fecha": datetime.now(),
        "canal": canal,
        "notas": notas,
        "resultado": resultado
    })


def obtener_logs_recientes(limite=30):
    db = get_mongo_db()
    return list(db.logs_sistema.find({}, {"_id": 0}).sort("timestamp", -1).limit(limite))
