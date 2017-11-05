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

# Fake User while login is not implemented:

login_session = {'user_id': 2}

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
    catalog = session.query(Catalog).order_by(asc(Catalog.name))
    #if 'username' not in login_session:
    #    return render_template('publicCatalog.html', catalog=catalog)
    #else:
    return render_template('catalog.html', catalog=catalog)


# Create a new category
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCatalog():
    #if 'username' not in login_session:
    #    return redirect('/login')
    if request.method == 'POST':
        newCatalog = Catalog(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newCatalog)
        flash('New Team %s Successfully Created' % newCatalog.name)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newCatalog.html')


# Edit a category
@app.route('/catalog/<int:catalog_id>/edit/', methods=['GET', 'POST'])
def editCatalog(catalog_id):
    editedCatalog = session.query(
        Catalog).filter_by(id=catalog_id).one()
    #if 'username' not in login_session:
    #    return redirect('/login')
    if editedCatalog.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this team. Please create your own team in order to edit.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedCatalog.name = request.form['name']
            flash('Team Successfully Edited %s' % editedCatalog.name)
            return redirect(url_for('showCatalog'))
    else:
        return render_template('editCatalog.html', catalog=editedCatalog)


# Delete a category
@app.route('/catalog/<int:catalog_id>/delete/', methods=['GET', 'POST'])
def deleteCatalog(catalog_id):
    catalogToDelete = session.query(
        Catalog).filter_by(id=catalog_id).one()
    #if 'username' not in login_session:
    #    return redirect('/login')
    if catalogToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this team. Please create your own team in order to delete.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(catalogToDelete)
        flash('%s Successfully Deleted' % catalogToDelete.name)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deleteCatalog.html', catalog=catalogToDelete)


# Show a category details
@app.route('/catalog/<int:catalog_id>/')
def showCategory(catalog_id):
    category = session.query(Catalog).filter_by(id=catalog_id).one()
    creator = 'test' #getUserInfo(catalog.user_id)
    items = session.query(CategoryItem).filter_by(
        catalog_id=catalog_id).all()
    #if 'username' not in login_session or creator.id != login_session['user_id']:
    #    return render_template('publicCategoryItems.html', items=items, category=category, creator=creator)
    #else:
    return render_template('categoryItems.html', items=items, category=category, creator=creator)


# Create a new category item
@app.route('/catalog/<int:catalog_id>/new/', methods=['GET', 'POST'])
def newCategoryItem(catalog_id):
    #if 'username' not in login_session:
    #    return redirect('/login')
    category = session.query(Catalog).filter_by(id=catalog_id).one()
    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() {alert('You are not authorized to add players to this team. Please create your own team in order to add players.');}</script><body onload='myFunction()'>"
        if request.method == 'POST':
            newCategoryItem = CategoryItem(name=request.form['name'], description=request.form['description'], catalog_id=catalog_id, user_id=category.user_id)
            session.add(newCategoryItem)
            session.commit()
            flash('New Player %s Successfully Created' % (newCategoryItem.name))
            return redirect(url_for('showCategory', catalog_id=catalog_id))
    else:
        return render_template('newCategoryItem.html', catalog_id=catalog_id)


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
