from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from . import db, endpoint

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    db.check_db_connection()
    db.db_init()
    app.register_blueprint(endpoint.endpoint)
    return app
