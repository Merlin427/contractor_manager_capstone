import os
SECRET_KEY = 'asdadasdasdasdasdasdias987das7dsadasdasd'
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgres://danievanrensburg:Danie427*@localhost:5432/capstone'
