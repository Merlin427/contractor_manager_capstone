#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import os
from flask import Flask, request, abort, jsonify, render_template, redirect, url_for, abort, jsonify, session
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
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
import json
from functools import wraps
import http.client
from auth.auth import AuthError, requires_auth
from models import *
import constants
#----------------------------------------------------------------------------#
# App Config
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
CORS(app)
migrate = Migrate(app, db)


AUTH0_CLIENT_ID = 'zWJfWgsOelcUY1yYwupvofc2oCr7JO52'
AUTH0_CLIENT_SECRET = 'YBV-ywAAlOWdLmJQaokgRJqeIdIEfmfINcqYkRpDliy9SojmXCxZ1VEjT3yTb-6p'
AUTH0_CALLBACK_URL = 'http://localhost:5000/callback'
AUTH0_DOMAIN = 'dvcoffee.us.auth0.com'
AUTH0_AUDIENCE = 'http://localhost:5000'
PROFILE_KEY = 'profile'
SECRET_KEY = 'YBV-ywAAlOWdLmJQaokgRJqeIdIEfmfINcqYkRpDliy9SojmXCxZ1VEjT3yTb-6p'
JWT_PAYLOAD = 'jwt_payload'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'http://localhost:5000'
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

#----------------------------------------------------------------------------#
# Filters (From Fyyur Project)
#----------------------------------------------------------------------------#
def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers
#----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/login.html')


@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)

@app.route('/logout')
def logout():
    session.clear()
    params = {'returnTo': url_for('index', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


@app.route('/callback')
def callback_handling():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')


    userinfo = resp.json()
    print(userinfo)

    session[constants.JWT_PAYLOAD] = userinfo
    session[constants.PROFILE_KEY] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }

    return redirect('/dashboard')



@app.route('/dashboard')
def dashboard():

    return render_template('pages/dashboard.html')




@app.route('/home')
@requires_auth('get:anything')
def home(payload):

    return render_template('pages/home.html')

@app.route('/contractors', methods=['GET'])
@requires_auth('get:anything')
def contractors(payload):
    contractors=Contractor.query.all()
    data=[]
    for contractor in contractors:
        data.append({
        "id": contractor.id,
        "name": contractor.name
        })

    return render_template('pages/contractors.html', contractors=data)



@app.route('/contractors/<int:contractor_id>')
@requires_auth('get:anything')
def show_contractor(payload, contractor_id):
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



@app.route('/contractors/create', methods=['POST'])
@requires_auth('post:anything')
def add_contractor(payload):

    form = ContractorForm(request.form, meta={"csrf": False})

    name = form.name.data.strip()
    phone = form.phone.data.strip()

    if not form.validate():
        abort(404)

    else:
        insert_error = False
        try:

            new_contractor = Contractor(name=name, phone=phone)

            db.session.add(new_contractor)
            db.session.commit()

        except Exception as e:
            insert_error = True
            print(f'Exception "{e}" in add_contractor()')
            db.session.rollback()
        finally:
            db.session.close()

        if not insert_error:
            return redirect(url_for('contractors'))


@app.route('/contractors/<int:contractor_id>/delete', methods=['GET'])
@requires_auth('delete:anything')
def delete_contractor(payload, contractor_id):
    error = False
    contractor = Contractor.query.get(contractor_id)

    try:
        db.session.delete(contractor)
        db.session.commit()
    except:
        db.session.rollback()
        error = True

    finally:
        db.session.close()

    if error:
        print("error in delete_contractor")
        abort(500)

    else:
        return redirect(url_for('contractors'))


@app.route('/contractors/<int:contractor_id>/edit', methods=['GET'])
@requires_auth('get:anything')
def edit_contractor(payload, contractor_id):

    contractor= Contractor.query.get(contractor_id)

    if not contractor:
        return redirect(url_for('index'))

    else:
        form = ContractorForm(obj=contractor)

    contractor = {
        "id": contractor.id,
        "name": contractor.name,
        "phone": contractor.phone
    }
    return render_template('forms/edit_contractor.html', form=form, contractor=contractor)



@app.route('/contractors/<int:contractor_id>/edit', methods=['POST'])
@requires_auth('patch:anything')
def edit_contractor_submission(payload,contractor_id):
    form = ContractorForm(request.form, meta={"csrf": False})

    name = form.name.data.strip()
    phone = form.phone.data.strip()

    if not form.validate():
        abort(404)

    else:
        update_error = False
        try:
            contractor=Contractor.query.get(contractor_id)
            contractor.name = name
            contractor.phone = phone


            db.session.commit()

        except Exception as e:
            update_error = True
            print(f'Exception "{e}" in add_contractor()')
            db.session.rollback()
        finally:
            db.session.close()

        if not update_error:
            return redirect(url_for('contractors'))




@app.route('/clients', methods=['GET'])
@requires_auth('get:anything')
def clients(payload):
    clients=Client.query.all()
    data=[]
    for client in clients:
        data.append({
        "id": client.id,
        "name": client.name
        })

    print(data)
    return render_template('pages/clients.html', clients=data)


@app.route('/clients/<int:client_id>')
@requires_auth('get:anything')
def show_client(payload, client_id):
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


@app.route('/clients/create', methods=['POST'])
@requires_auth('post:anything')
def add_client(payload):

    form = ClientForm(request.form, meta={"csrf": False})

    name = form.name.data.strip()
    phone = form.phone.data.strip()
    address = form.address.data.strip()

    if not form.validate():
        abort(404)

    else:
        insert_error = False
        try:

            new_client = Client(name=name, phone=phone, address=address)

            db.session.add(new_client)
            db.session.commit()

        except Exception as e:
            insert_error = True
            print(f'Exception "{e}" in add_client()')
            db.session.rollback()
        finally:
            db.session.close()

        if not insert_error:
            return redirect(url_for('clients'))


@app.route('/clients/<int:client_id>/delete', methods=['GET'])
@requires_auth('delete:anything')
def delete_client(payload, client_id):
    error = False
    client = Client.query.get(client_id)

    try:
        db.session.delete(client)
        db.session.commit()
    except:
        db.session.rollback()
        error = True

    finally:
        db.session.close()

    if error:
        print("error in delete_client")
        abort(500)

    else:
        return redirect(url_for('clients'))


@app.route('/clients/<int:client_id>/edit', methods=['GET'])
def edit_client(client_id):

    client= Client.query.get(client_id)

    if not client:
        return redirect(url_for('index'))

    else:
        form = ClientForm(obj=client)

    client = {
        "id": client.id,
        "name": client.name,
        "phone": client.phone,
        "address": client.address
    }
    return render_template('forms/edit_client.html', form=form, client=client)



@app.route('/clients/<int:client_id>/edit', methods=['POST'])
@requires_auth('patch:anything')
def edit_client_submission(payload, client_id):
    form = ClientForm(request.form, meta={"csrf": False})

    name = form.name.data.strip()
    phone = form.phone.data.strip()
    address = form.address.data.strip()

    if not form.validate():
        abort(404)

    else:
        update_error = False
        try:
            client=Client.query.get(client_id)
            client.name = name
            client.phone = phone
            client.address = address


            db.session.commit()

        except Exception as e:
            update_error = True
            print(f'Exception "{e}" in add_client_submission()')
            db.session.rollback()
        finally:
            db.session.close()

        if not update_error:
            return redirect(url_for('clients'))


@app.route('/jobs', methods=['GET'])
@requires_auth('get:anything')
def jobs(payload):
    jobs=Job.query.all()
    data=[]
    for job in jobs:
        data.append({
        "id": job.id,
        "client_id": job.client.id,
        "client_name": job.client.name,
        "client_address": job.client.address,
        "contractor_name": job.contractor.name,
        "start_time": format_datetime(str(job.start_time))
        })

    print(data)
    return render_template('pages/jobs.html', jobs=data)


@app.route('/jobs/<int:job_id>', methods=['GET'])
@requires_auth('get:anything')
def show_job(payload, job_id):
    job = Job.query.get(job_id)

    if not job:
        return redirect(url_for('index'))

    else:

        data={
        "id": job_id,
        "client": job.client.name,
        "address": job.client.address,
        "phone": job.client.phone,
        "contractor": job.contractor.name,
        "start_time": format_datetime(str(job.start_time))
        }

    print(data)

    return render_template('pages/show_jobs.html', job=data)

@app.route('/jobs/create', methods=['GET'])
def add_job_form():
  form = JobForm()
  return render_template('forms/new_job.html', form=form)


@app.route('/jobs/create', methods=['POST'])
@requires_auth('post:anything')
def create_job(payload):

    form= JobForm()

    contractor_id = form.contractor_id.data.strip()
    client_id = form.client_id.data.strip()
    start_time = form.start_time.data

    insert_error=False

    try:
        new_job = Job(start_time=start_time, contractor_id=contractor_id, client_id=client_id)
        db.session.add(new_job)
        db.session.commit()
    except Exception as e:
        insert_error=True
        print(f'Exception "{e}" in create_job')
        db.session.rollback()
    finally:
        db.session.close()
    if insert_error:

        print("Error in create_job")
    else:
        return redirect(url_for('jobs'))


@app.route('/jobs/<int:job_id>/edit', methods=['GET'])
def edit_job(job_id):

    job= Job.query.get(job_id)

    if not job:
        return redirect(url_for('index'))

    else:
        form = JobForm(obj=job)

    job = {
        "id": job.id,
        "client_id": job.client.id,
        "contractor_id": job.contractor.id

    }
    return render_template('forms/edit_job.html', form=form, job=job)



@app.route('/jobs/<int:job_id>/edit', methods=['POST'])
@requires_auth('patch:anything')
def edit_job_submission(payload, job_id):
    form = JobForm(request.form, meta={"csrf": False})

    contractor_id = form.contractor_id.data.strip()
    client_id = form.client_id.data.strip()
    start_time = form.start_time.data

    if not form.validate():
        abort(404)

    else:
        update_error = False
        try:
            job=Job.query.get(job_id)
            job.client_id = client_id
            job.contractor_id = contractor_id
            job.start_time = start_time



            db.session.commit()

        except Exception as e:
            update_error = True
            print(f'Exception "{e}" in edit_job_submission()')
            db.session.rollback()
        finally:
            db.session.close()

        if not update_error:
            return redirect(url_for('jobs'))


@app.route('/jobs/<int:job_id>/delete', methods=['GET'])
@requires_auth('delte:anything')
def delete_job(payload, job_id):
    error = False
    job = Job.query.get(job_id)

    try:
        db.session.delete(job)
        db.session.commit()
    except:
        db.session.rollback()
        error = True

    finally:
        db.session.close()

    if error:
        print("error in delete_job")
        abort(500)

    else:
        return redirect(url_for('jobs'))

#----------------------------------------------------------------------------#
# Error Handlers
#----------------------------------------------------------------------------#

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'Bad Request'
    }), 400

@app.errorhandler(401)
def unauthorised(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unauthorised'
    }), 401

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": 'Not Found'
    }), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'Internal Server Error'
    }), 500
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), 401
'''

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
