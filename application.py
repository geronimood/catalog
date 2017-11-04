#!/usr/bin/env python2.7.12  # shebang line for the used Python version

from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, CategoryItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import OAuth2Credentials
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# Setting Client ID and application name

#CLIENT_ID = json.loads(
#    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Category Item Catalog"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/login')
def showLogin():
    return 'Login page'

@app.route('/gconnect', methods=['POST'])
def gconnect():
    return 'Google connect page'

@app.route('/user/<int:user_id>/')
def show_user(user_id):
    return 'Shows page with User ID #%s' % user_id

@app.route('/gdisconnect')
def gdisconnect():
    return 'disconnects logged in user'

# Show all categories
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    return 'list of all categories'


# Create a new category
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCatalog():
    return 'page to enter new category'


# Edit a category
@app.route('/catalog/<int:catalog_id>/edit/', methods=['GET', 'POST'])
def editCatalog(catalog_id):
    return 'edit category'


# Delete a category
@app.route('/catalog/<int:catalog_id>/delete/', methods=['GET', 'POST'])
def deleteCatalog(catalog_id):
    return 'delete category'


# Show a category details
@app.route('/catalog/<int:catalog_id>/')
def showCategory(catalog_id):
    return 'show category details'


# Create a new category item
@app.route('/catalog/<int:catalog_id>/new/', methods=['GET', 'POST'])
def newCategoryItem(catalog_id):
    return 'create new category item'


# Edit a category item
@app.route('/catalog/<int:catalog_id>/<int:item_id>/edit', methods=['GET', 'POST'])
def editCategoryItem(catalog_id, item_id):
    return 'edit category item'


# Delete a category item
@app.route('/catalog/<int:catalog_id>/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteCategoryItem(catalog_id, item_id):
    return 'delete category item'



# Execute file if it is in the main directory and run the webserver on localhost port 8000
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
