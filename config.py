import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
DATABASE_NAME = "fyyur"
username = 'ribo'
password = 'mfc'
url = 'localhost:5432'

# Done IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = f'postgresql://{username}:{password}@{url}/{DATABASE_NAME}'

# Remove warnings
SQLALCHEMY_TRACK_MODIFICATIONS = False
