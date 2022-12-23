import os
from flask import Flask, render_template

import logging.config

# Logging configuration so all messages have the same format
def configure_logging():
    logging.config.dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                }
            },
            "handlers": {
                "wsgi": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "default",
                }
            },
            "root": {"level": "INFO", "handlers": ["wsgi"]},
        }
    )

# GENERAL ERROR HANDLERS
def page_not_found(e):
    return render_template('errors/404.html'), 404


# APPLICATION FACTORY
def create_app(test_config=None):
    
    # logging config first of all
    configure_logging()

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
            SECRET_KEY='dev',
            DATABASE=os.path.join(app.instance_path, 'quizzer.db'),
            QDB=os.path.join(app.instance_path, 'qdb.json')
            )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)

    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # register error handlers
    app.register_error_handler(404, page_not_found)

    # register database
    from . import db
    db.init_app(app)

    from .quiz import qdb
    qdb.init_app(app)
    
    # register blueprints
    from . import auth
    app.register_blueprint(auth.bp)

    from . import news
    app.register_blueprint(news.bp)
    app.add_url_rule('/', endpoint='index')

    from .quiz import quiz
    app.register_blueprint(quiz)

    # telling the logger it has started
    app.logger.info(f"New app started in {app.config['ENVIRONMENT']}")
    
    return app


