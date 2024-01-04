from flask import Flask, g
import os

def create_app():
    app = Flask(__name__, template_folder="templates", static_url_path="/static")
    

    app.config.from_mapping(
        SECRET_KEY = os.environ.get('SECRET_KEY') 
    )
    
    from . import db
    
    
    from . import home
    from . import auth
    from . import about
    
    db.init_app(app)

    app.register_blueprint(home.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(about.bp)


    return app
