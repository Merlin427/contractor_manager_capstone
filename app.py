import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_moment import Moment

from models import *


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
CORS(app)
migrate = Migrate(app, db)



@app.route('/')
def index():
    return 'hello'


if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
