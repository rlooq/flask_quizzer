import sqlite3
import click
from flask import current_app, g


def get_db():
    """Returns a g.db connection if not present in g"""
    if 'db' not in g:
        g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
                )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """Pops db from g if present"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Gets g.db and creates tables from schema.sql"""
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """CLI command to clear the existing data and create new tables"""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    """Registers CLI command in app after making sure db is closed"""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
