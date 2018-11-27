from flask import Flask, render_template, request, redirect
from flask import url_for, flash, jsonify
# import for sqlalchemy and database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from catalog_database_setup import Base, Category, Item, User
# import for anti-forgery state token.
from flask import session as login_session
import random
import string
# import for Gconnect
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# read client id fron client_secrets.json
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "catalog"

# database engine
engine = create_engine('sqlite:///categories.db')
Base.metadata.bind = engine

# database session
DBSession = sessionmaker(bind=engine)
session = DBSession()


# log in to login user
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# google connection
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
        response = make_response(
                    json.dumps('Current user is already connected.'), 200)
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
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; '
    output == "height: 300px;"
    output += "border-radius: 150px;"
    output += "-webkit-border-radius: 150px;"
    output += '-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# google disconnect
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
                    json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is ', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
                    json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON
@app.route('/catalog/JSON')
def cataloJSON():
    categories = session.query(Category).all()
    categoriesJSON = [c.serialize for c in categories]
    for categoriesItem in range(len(categoriesJSON)):
            itemsJSON = [i.serialize
                for i in session.query(Item).filter_by(category_id = categoriesJSON[categoriesItem]["id"]).all()]
            if itemsJSON:
                categoriesJSON[categoriesItem]["Item"] = itemsJSON
    return jsonify(Category = categoriesJSON)


# home page display all categories and last added items
@app.route('/')
@app.route('/catalog')
def catalog():
    categories = session.query(Category).all()
    latestItems = session.query(Item).order_by(Item.id.desc()).limit(5)
    if 'username' not in login_session:
        return render_template('publicCatalog.html', categories = categories, latestItems = latestItems)
    else:
        return render_template('catalog.html', categories = categories, latestItems = latestItems)


# catalogItems display items that belong to a specific category
@app.route('/catalog/<string:category_name>/items')
def categoryItems(category_name):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name = category_name).one()
    items = session.query(Item).filter_by(category_id = category.id).all()
    return render_template('categoryItems.html', categories = categories, category = category, items = items)


# itemDescription display a specific item information
@app.route('/catalog/<string:category_name>/<string:item_name>')
def itemDescription(category_name, item_name):
    item = session.query(Item).filter_by(name = item_name).one()
    creator = getUserInfo(item.user_id)
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('puplicItemDescription.html', item = item)
    else:
        return render_template('itemDescription.html', item = item)


# newItem add new item
@app.route('/catalog/new', methods=['GET', 'POST'])
def newItem():
    categories = session.query(Category).all()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        category = session.query(Category).filter_by(name=request.form['category']).one()
        newItem = Item(name = request.form['title'],
                       description = request.form['description'],
                       category_id = category.id,
                       user_id = login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New %s  Item Successfully Created' % (newItem.name))
        return redirect(url_for('catalog'))
    return render_template('newItem.html', categories = categories)


# editItem edit a specific item
@app.route('/catalog/<string:item_name>/edit', methods=['GET', 'POST'])
def editItem(item_name):
    categories = session.query(Category).all()
    editedItem = session.query(Item).filter_by(name = item_name).one()
    categoryName = session.query(Category).filter_by(id = editedItem.category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedItem.user_id != login_session['user_id']:
        return """<script>function myFunction(){
                      alert('You are not authorized to edit this Item. Please create your own Item in order to edit.');
                                      }
                  </script>
                      <body onload='myFunction()'>"""
    if request.method == 'POST':
        if request.form['title']:
            editedItem.name = request.form['title']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category']:
            category = session.query(Category).filter_by(name=request.form['category']).one()
            editedItem.category_id = category.id
        session.add(editedItem)
        session.commit()
        flash('Menu Item Successfully Edited')
        newCategory = session.query(Category).filter_by(id = editedItem.category_id).one()
        return redirect(url_for('itemDescription', category_name = categoryName.name, item_name = editedItem.name))
    return render_template('editItem.html', categories = categories, editedItem = editedItem, categoryName = categoryName)


# deleteItem delete a specific item
@app.route('/catalog/<string:item_name>/delete', methods=['GET', 'POST'])
def deleteItem(item_name):
    deletedItem = session.query(Item).filter_by(name = item_name).one()
    if 'username' not in login_session:
        return redirect('/login')
        if deletedItem.user_id != login_session['user_id']:
            return """<script>function myFunction(){
                          alert('You are not authorized to delete this Item. Please create your own Item in order to delete.');
                                          }
                      </script>
                          <body onload='myFunction()'>"""
    if request.method == 'POST':
        session.delete(deletedItem)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('catalog'))
    return render_template('deleteItem.html', deletedItem = deletedItem)


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


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
