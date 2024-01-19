import pyodbc
import click
from flask import current_app, g
from flask.cli import with_appcontext
from .schema import instructions


def get_db():
    if not 'db' in g:
        host = current_app.config['DATABASE_HOST']
        database = current_app.config['DATABASE']
        username = current_app.config['DATABASE_USER']
        password = current_app.config['DATABASE_PASSWORD']
        connect_str = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={host};DATABASE={database};UID={username};PWD={password};timeout=20;TrustServerCertificate=yes'
        g.db = pyodbc.connect(connect_str)
        return g.db


def close_db(e: None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    for i in instructions:
        db.execute(i)
    db.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Base de datos inicializada con éxito ✅')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
