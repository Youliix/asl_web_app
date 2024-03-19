from dotenv import load_dotenv
load_dotenv()

import os

from flask import Flask, render_template
from flask_cors import CORS

import threading

from . import db

from .main import main
from .auth import auth
from .prediction import prediction
from .error import error

from . import cron_job

def create_app(test_config=None):
    
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, resources={r'/*': {'origins': 'http://127.0.0.1:8000'}})
    
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

    db.check_db_connection()
    db.db_init()

    t = threading.Thread(target=cron_job.run_scheduler)
    t.start()

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(prediction)
    app.register_blueprint(error)

    return app