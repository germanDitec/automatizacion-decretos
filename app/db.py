import pyodbc
from flask import current_app, g



def get_db():
    if not 'db' in g:
        host = "localhost"
        database = "Decretos"
        username = "sa"
        password = "!desarroll0"
        connect_str = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={host};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes'
        print("Conexión exitosa")
        g.db = pyodbc.connect(connect_str)
        return g.db

def close_db(e: None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
