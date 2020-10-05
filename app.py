import os
from flask import Flask, request, abort, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_moment import Moment
from datetime import date, datetime, time
from babel.dates import format_date, format_datetime, format_time
import dateutil.parser
import babel
from flask_wtf import Form
from forms import *

from models import *


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
CORS(app)
migrate = Migrate(app, db)


def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime



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



@app.route('/contractors/<int:contractor_id>')
def show_contractor(contractor_id):
    contractor = Contractor.query.get(contractor_id)

    if not contractor:
        return redirect(url_for('index'))

    else:

        data={
        "id": contractor_id,
        "name": contractor.name,
        "phone": contractor.phone
        }

    return render_template('pages/show_contractor.html', contractor=data)

@app.route('/contractors/create', methods=['GET'])
def add_contractor_form():
  form = ContractorForm()
  return render_template('forms/new_contractor.html', form=form)

@app.route('/clients', methods=['GET'])
def clients():
    clients=Client.query.all()
    data=[]
    for client in clients:
        data.append({
        "id": client.id,
        "name": client.name
        })

    return render_template('pages/clients.html', clients=data)


@app.route('/clients/<int:client_id>')
def show_client(client_id):
    client = Client.query.get(client_id)

    if not client:
        return redirect(url_for('index'))

    else:

        data={
        "id": client_id,
        "name": client.name,
        "phone": client.phone,
        "address": client.address
        }

    return render_template('pages/show_clients.html', client=data)


@app.route('/clients/create', methods=['GET'])
def add_client_form():
  form = ClientForm()
  return render_template('forms/new_client.html', form=form)


@app.route('/jobs', methods=['GET'])
def jobs():
    jobs=Job.query.all()
    data=[]
    for job in jobs:
        data.append({
        "client_id": job.client.id,
        "client_name": job.client.name,
        "client_address": job.client.address,
        "contractor_name": job.contractor.name,
        "start_time": format_datetime(str(job.start_time))
        })

    return render_template('pages/jobs.html', jobs=data)

@app.route('/jobs/create', methods=['GET'])
def add_job_form():
  form = JobForm()
  return render_template('forms/new_job.html', form=form)


if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
