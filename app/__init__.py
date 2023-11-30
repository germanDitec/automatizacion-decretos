from flask import Flask, g

def create_app():
    app = Flask(__name__, template_folder="templates", static_url_path="/static")
    from . import home
    app.register_blueprint(home.bp)
    return app
