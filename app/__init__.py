from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_cors import CORS
from . import endpoint
from . import db
from . import cron_job

import threading

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, resources={r'/*': {'origins': 'http://127.0.0.1:8000'}})
    db.check_db_connection()
    db.db_init()
    t = threading.Thread(target=cron_job.run_scheduler)
    t.start()
    app.register_blueprint(endpoint.endpoint)
    return app
