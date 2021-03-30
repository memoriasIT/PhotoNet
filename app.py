# Python standard libraries
import os
import sqlite3
from datetime import datetime
from functools import wraps
from bson import ObjectId

#  Flask
from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

# Database
import pymongo

# Set up app
SECRET_KEY = 'development key'
DEBUG = True
app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY

# Set up DB
uri = ''
client = pymongo.MongoClient(uri)
db = client.get_default_database()  
photos = db['photonet']


# Routes
from user import routes
from entity import routes



@app.route('/')
def home():
  try:
    if session['logged_in'] == True:
      return redirect(url_for('showDirectorio'))
  except:
    return render_template('home.html')

    

# Decorators
def login_required(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if 'logged_in' in session:
      return f(*args, **kwargs)
    else:
      return redirect('/')
  
  return wrap


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True, ssl_context="adhoc")
