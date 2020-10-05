import os
from flask import Flask, request, abort, jsonify, render_template
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
    return render_template('pages/home.html')

@app.route('/contractors', methods=['GET'])
def contractors():
    contractors=Contractor.query.all()
    data=[]
    for contractor in contractors:
        data.append({
        "id": contractor.id,
        "name": contractor.name
        })

    return render_template('pages/contractors.html', contractors=data)



if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
