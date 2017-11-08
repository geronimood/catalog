#!/usr/bin/env python2.7.12

from flask import Flask, render_template, request, redirect, jsonify, \
                  url_for, flash
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

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Basketball Teams"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Route for login
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Route for google oauth2 authentication
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in")
    print "done!"
    return output


# User Helper Functions

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session

@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        flash('Successfully disconnected.')
        return redirect(url_for('showCatalog'))

    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Show all categories
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    catalog = session.query(Catalog).order_by(asc(Catalog.name))
    if 'username' not in login_session:
        return render_template('publicCatalog.html', catalog=catalog)
    else:
        return render_template('catalog.html', catalog=catalog)


# Create a new category
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCatalog():
    if 'username' not in login_session:
        return redirect('/login')
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
    if 'username' not in login_session:
        return redirect('/login')
    if editedCatalog.user_id != login_session['user_id']:
        flash('Not authorized to edit this team. Create your own team \
               to edit.')
        return redirect(url_for('showCatalog'))
    if request.method == 'POST':
        if request.form['name']:
            editedCatalog.name = request.form['name']
            flash('Team Successfully Edited %s' % editedCatalog.name)
            return redirect(url_for('showCatalog'))
    else:
        return render_template('editCatalog.html', catalog=editedCatalog,
                               catalog_id=catalog_id)


# Delete a category
@app.route('/catalog/<int:catalog_id>/delete/', methods=['GET', 'POST'])
def deleteCatalog(catalog_id):
    catalogToDelete = session.query(
        Catalog).filter_by(id=catalog_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if catalogToDelete.user_id != login_session['user_id']:
        flash('Not authorized to delete this team. Create own team to delete.')
        return redirect(url_for('showCatalog'))
    if request.method == 'POST':
        session.delete(catalogToDelete)
        flash('%s Successfully Deleted' % catalogToDelete.name)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deleteCatalog.html', catalog=catalogToDelete,
                               catalog_id=catalog_id)


# Show a category details
@app.route('/catalog/<int:catalog_id>/')
def showCategory(catalog_id):
    category = session.query(Catalog).filter_by(id=catalog_id).one()
    creator = getUserInfo(category.user_id)
    items = session.query(CategoryItem).filter_by(
        catalog_id=catalog_id).all()
    if 'username' not in login_session or \
       creator.id != login_session['user_id']:
        return render_template('publicCategoryItems.html', items=items,
                               category=category, creator=creator)
    else:
        return render_template('categoryItems.html', items=items,
                               category=category, creator=creator)


# Create a new category item
@app.route('/catalog/<int:catalog_id>/new/', methods=['GET', 'POST'])
def newCategoryItem(catalog_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Catalog).filter_by(id=catalog_id).one()
    if login_session['user_id'] != category.user_id:
        flash('Not authorized to add players to this team. Create your own team \
               in order to add players.')
        return redirect(url_for('showCategory', catalog_id=catalog_id))
    if request.method == 'POST':
        newCategoryItem = CategoryItem(
                          name=request.form['name'],
                          description=request.form['description'],
                          catalog_id=catalog_id, user_id=category.user_id)
        session.add(newCategoryItem)
        session.commit()
        flash('New Player %s Successfully Created' % (newCategoryItem.name))
        return redirect(url_for('showCategory', catalog_id=catalog_id))
    else:
        return render_template('newCategoryItem.html', catalog_id=catalog_id)


# Edit a category item
@app.route('/catalog/<int:catalog_id>/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editCategoryItem(catalog_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    edCategoryItem = session.query(CategoryItem).filter_by(id=item_id).one()
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    if login_session['user_id'] != catalog.user_id:
        flash('Not authorized to edit players to this team. Create your own \
               team in order to edit players.')
        return redirect(url_for('showCategory', catalog_id=catalog_id))
    if request.method == 'POST':
        if request.form['name']:
            edCategoryItem.name = request.form['name']
        if request.form['description']:
            edCategoryItem.description = request.form['description']
        session.add(edCategoryItem)
        session.commit()
        flash('Player Successfully Edited')
        return redirect(url_for('showCategory', catalog_id=catalog_id))
    else:
        return render_template('editCategoryItem.html',
                               catalog_id=catalog_id, item_id=item_id,
                               item=edCategoryItem)


# Delete a category item
@app.route('/catalog/<int:catalog_id>/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteCategoryItem(catalog_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    itemToDelete = session.query(CategoryItem).filter_by(id=item_id).one()
    if login_session['user_id'] != catalog.user_id:
        flash('Not authorized to delete players to this team. Create your own \
               team in order to delete players.')
        return redirect(url_for('showCategory', catalog_id=catalog_id))
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Player Successfully Deleted')
        return redirect(url_for('showCategory', catalog_id=catalog_id))
    else:
        return render_template('deleteCategoryItem.html', item=itemToDelete,
                               catalog_id=catalog_id)


# JSON APIs to view Catalog and Category Information
@app.route('/catalog/JSON')
def catalogJSON():
    catalog = session.query(Catalog).all()
    return jsonify(catalog=[cat.serialize for cat in catalog])


@app.route('/catalog/<int:catalog_id>/JSON')
def categoryJSON(catalog_id):
    category = session.query(Catalog).filter_by(id=catalog_id).one()
    items = session.query(CategoryItem).filter_by(
        catalog_id=catalog_id).all()
    return jsonify(category=[i.serialize for i in items])


# Execute file only if it is in the main directory
# and run the webserver on localhost port 8000
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
