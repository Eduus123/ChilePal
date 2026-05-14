import os
import mysql.connector
from config import MYSQL_CONFIG, MYSQL_DATABASE


def inicializar_mysql():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=MYSQL_CONFIG["password"]
        )
        cursor = conn.cursor()

        cursor.execute(f"""
            CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}
            CHARACTER SET utf8mb4
            COLLATE utf8mb4_spanish_ci
        """)

        cursor.execute(f"""
            CREATE USER IF NOT EXISTS
            'chilepal_user'@'localhost'
            IDENTIFIED BY '{MYSQL_CONFIG["password"]}'
        """)
        cursor.execute(f"""
            ALTER USER 'chilepal_user'@'localhost'
            IDENTIFIED BY '{MYSQL_CONFIG["password"]}'
        """)

        cursor.execute(f"""
            GRANT ALL PRIVILEGES
            ON {MYSQL_DATABASE}.*
            TO 'chilepal_user'@'localhost'
        """)

        cursor.execute("FLUSH PRIVILEGES")
        cursor.execute(f"USE {MYSQL_DATABASE}")

        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")

        if os.path.exists(schema_path):
            with open(schema_path, "r", encoding="utf-8") as f:
                sql_script = f.read()

            for statement in sql_script.split(";"):
                statement = statement.strip()
                if statement:
                    try:
                        cursor.execute(statement)
                    except mysql.connector.Error as e:
                        if e.errno != 1050:
                            print(f"⚠ {e}")

            conn.commit()
            print("✔ MySQL inicializado correctamente.")
        else:
            print("⚠ No se encontró schema.sql")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"✖ Error MySQL: {e}")


def get_mysql_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)


def query(sql, params=None, fetch=False, fetchone=False):
    connection = get_mysql_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql, params or ())

    sql_lower = sql.strip().lower()

    if fetch or fetchone or sql_lower.startswith("select"):
        result = cursor.fetchone() if fetchone else cursor.fetchall()
    else:
        connection.commit()
        result = cursor.lastrowid

    cursor.close()
    connection.close()
    return result


def query_one(sql, params=None):
    return query(sql, params, fetchone=True)


def execute(sql, params=None):
    return query(sql, params)
