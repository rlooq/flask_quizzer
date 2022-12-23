from tinydb import TinyDB, Query
from flask import current_app, g
import click

def get_qdb():
    """Returns a g.qdb TinyDB object if not present in g"""
    if 'qdb' not in g:
        g.qdb = TinyDB(current_app.config['QDB'])
    return g.qdb


def close_qdb(e=None):
    """Pops qdb from g if present"""
    qdb = g.pop('qdb', None)


def init_app(app):
    """Making sure db is popped at the end of the context"""
    app.teardown_appcontext(close_qdb)