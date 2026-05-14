from database.mysql_connection import query, query_one
import uuid


def registrar_pago(id_pedido, monto, metodo):
    comprobante = f"COMP-{uuid.uuid4().hex[:8].upper()}"
    query(
        "INSERT INTO pagos (id_pedido, monto, metodo, numero_comprobante) VALUES (%s, %s, %s, %s)",
        (id_pedido, monto, metodo, comprobante),
        fetch=False
    )
    return comprobante


def obtener_total_ventas():
    result = query_one("SELECT COALESCE(SUM(monto), 0) AS total FROM pagos")
    return result["total"] if result else 0
