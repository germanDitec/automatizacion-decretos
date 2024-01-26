from flask import Flask, g, render_template, session
from flask_session import Session
from flask_mail import Mail
import os


def create_app():
    app = Flask(__name__, template_folder="templates",
                static_url_path="/static")

    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        DATABASE_HOST=os.environ.get('DATABASE_HOST'),
        DATABASE_USER=os.environ.get('DATABASE_USER'),
        DATABASE_PASSWORD=os.environ.get('DATABASE_PASSWORD'),
        DATABASE=os.environ.get('DATABASE'),
        MAIL_SERVER=os.environ.get('MAIL_SERVER'),
        MAIL_PORT=587,
        MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
        MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD'),
        MAIL_DEFAULT_SENDER=os.environ.get('MAIL_DEFAULT_SENDER'),
        MAIL_USE_TLS=True,
        MAIL_USE_SSL=False,
    )

    mail = Mail(app)

    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False

    Session(app)

    from . import home
    from . import auth
    from . import about
    from . import db

    db.init_app(app)

    @app.errorhandler(400)
    def not_found(e):
        return render_template('errors/400.html'), 400

    app.register_blueprint(home.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(about.bp)

    return app
