from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_cors import CORS
from . import db, endpoint

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, resources={r'/*': {'origins': ['https://asl-web-app.onrender.com']}})
    db.check_db_connection()
    db.db_init()
    app.register_blueprint(endpoint.endpoint)
    return app
