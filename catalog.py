from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import make_response
from flask import session as login_session
from flask_wtf.csrf import CSRFProtect, CSRFError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CatalogItem, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from functools import wraps
import random
import string
import requests
import httplib2
import json


app = Flask(__name__)

with app.open_resource('client_secrets.json') as jsonFile:
    CLIENT_ID = json.load(jsonFile)['web']['client_id']

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Enable CSRF Protection
CSRFProtect(app)


# Login required decorator
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('showLogin'))
        else:
            return func(*args, **kwargs)
    return wrapper


######################
# JSON API Section
######################


@app.route('/api/v1/catalog/')
def showCatalogJSON():
    """ API that returns JSON with all catalog items registered """
    allItems = session.query(CatalogItem).order_by(CatalogItem.id.asc())
    return jsonify(Items=[item.serialize for item in allItems])


@app.route('/api/v1/categories/')
def showCategoryJSON():
    """ API that returns JSON with all categories registered """
    categories = session.query(Category).all()
    return jsonify(Categories=[item.serialize for item in categories])


@app.route('/api/v1/catalog/<int:catalog_id>')
@app.route('/api/v1/catalog/<int:catalog_id>/items')
def detailCategoryJSON(catalog_id):
    """ API that returns JSON with all catalog item of the given category """
    categoryItems = session.query(CatalogItem).filter_by(
        category_id=catalog_id).order_by(CatalogItem.id.asc()).all()
    return jsonify(Items=[item.serialize for item in categoryItems])


@app.route('/api/v1/catalog/<int:catalog_id>/item/<int:item_id>')
def detailItemJSON(catalog_id, item_id):
    """ API that returns JSON with the item detail of the given item id """
    item = session.query(CatalogItem).filter_by(id=item_id).first()
    return jsonify(Item=item.serialize)


##################################
# Catalog Read Operation Section
##################################


@app.route('/')
@app.route('/catalog/')
def showCategory():
    """ Returns the page with all categories and latest items"""
    categories = session.query(Category).all()

    # Get latest items ordered by creation date (max 10 items)
    categoryItems = session.query(CatalogItem).order_by(
        CatalogItem.id.desc()).limit(10)
    return render_template(
        'index.html', categories=categories,
        categoryName='Latest Items', categoryItems=categoryItems)


@app.route('/catalog/<int:catalog_id>')
@app.route('/catalog/<int:catalog_id>/items')
def detailCategory(catalog_id):
    """ Returns the page with all categories and the ordered catalog items
        of the requested category """
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=catalog_id).first()

    # Case no results returned due invalid id, redirect to main screen
    if category is None:
        return redirect(url_for('showCategory'))
    categoryName = category.name
    categoryId = category.id
    categoryItems = session.query(CatalogItem).filter_by(
        category_id=catalog_id).order_by(CatalogItem.id.desc())
    return render_template(
        'index.html', categories=categories, categoryItems=categoryItems,
        categoryName=categoryName, categoryId=categoryId)


@app.route('/catalog/<int:catalog_id>/item/<int:item_id>')
def detailItem(catalog_id, item_id):
    """ Returns the page with the details of the requested item"""
    catalogItem = session.query(CatalogItem).filter_by(id=item_id).first()

    # Case no results returned due invalid id, redirect to main screen
    if catalogItem is None:
        return redirect(url_for('showCategory'))
    creator = getUserInfo(catalogItem.user_id)

    # Flag that identifies if Edit/Delete button will appear for logged users
    if login_session.get('user_id') == creator.id:
        canEdit = True
    else:
        canEdit = False
    return render_template(
        'detail_item.html', catalog_id=catalog_id, catalogItem=catalogItem,
        creator=creator, canEdit=canEdit)


##################################
# Catalog Update Operations Section
##################################


@app.route(
    '/catalog/<int:catalog_id>/item/<int:item_id>/edit',
    methods=['GET', 'POST'])
@login_required
def editItem(catalog_id, item_id):
    """ Edit page - Responsible for update the requested item"""

    editedItem = session.query(CatalogItem).filter_by(id=item_id).first()

    # Case no results returned due invalid id, redirect to main screen
    if editedItem is None:
        return redirect(url_for('showCategory'))
    # Only the owner of the item can edit the item
    if editedItem.user_id != login_session.get('user_id'):
        return "<script>function myFunction() {alert('You are not authorized to edit this item. Please create your own item in order to edit.');}</script><body onload='myFunction()''>"  # noqa
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['image_url']:
            editedItem.image_url = request.form['image_url']
        session.add(editedItem)
        session.commit()
        return redirect(url_for(
            'detailItem', catalog_id=catalog_id, item_id=item_id))
    else:
        return render_template(
            'edit_item.html', catalog_id=catalog_id, item_id=item_id,
            item=editedItem)


##################################
# Catalog Create Operation Section
##################################


@app.route(
    '/catalog/item/create',
    methods=['GET', 'POST'])
@login_required
def createItem():
    """Create page - Responsible for create a new item of selected category"""

    categories = session.query(Category).all()
    if request.method == 'POST':
        newItem = CatalogItem(
            name=request.form['name'],
            description=request.form['description'],
            image_url=request.form['image_url'],
            category_id=request.form['category'],
            user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()

        return redirect(url_for('showCategory'))
    else:
        return render_template('create_item.html', categories=categories)


##################################
# Catalog Delete Operation Section
##################################


@app.route('/catalog/<int:catalog_id>/item/<int:item_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteItem(catalog_id, item_id):
    """ Delete page - Responsible for delete the requested item """

    itemToDelete = session.query(CatalogItem).filter_by(id=item_id).first()

    # Case no results returned due invalid id, redirect to main screen
    if itemToDelete is None:
        return redirect(url_for('showCategory'))
    # Only the owner of the item can delete the item
    if itemToDelete.user_id != login_session.get('user_id'):
        return "<script>function myFunction() {alert('You are not authorized to delete this item. Please create your own item in order to delete.');}</script><body onload='myFunction()''>"  # noqa
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showCategory'))
    else:
        return render_template('delete_item.html', item=itemToDelete)


##################################
# Login Handling Section
##################################


@app.route('/login')
def showLogin():
    """ Generate login state session and returns the login page """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """ Method responsible for making the login using the GOOGLE account """

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
        print login_session
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

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    login_session['provider'] = 'google'

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

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
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '  # noqa
    return output


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """ Method responsible for making the login using a FACEBOOK account """

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (  # noqa
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"

    # Parse result to retrieve token
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
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
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '  # noqa

    return output


def createUser(login_session):
    """ Method responsible for create an user in the database """
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).first()
    return user.id


def getUserInfo(user_id):
    """ Method responsible for retrieve logged user details """
    user = session.query(User).filter_by(id=user_id).first()
    return user


def getUserID(email):
    """ Method responsible for retrieve logged user id """
    try:
        user = session.query(User).filter_by(email=email).first()
        return user.id
    except:
        return None


##################################
# Disconnect Handling Section
##################################


@app.route('/gdisconnect')
def gdisconnect():
    """ Method responsible for disconnect from google provider """
    access_token = login_session.get('credentials')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['credentials']  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] != '200':
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 401))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/fbdisconnect')
def fbdisconnect():
    """ Method responsible for disconnect from facebook provider """
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)  # noqa
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/disconnect')
def disconnect():
    """ Method responsible for logout according to the provider
        user is connected """
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        return redirect(url_for('showCategory'))
    else:
        return redirect(url_for('showCategory'))


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    """Error raised when CSRF validation fails"""
    response = make_response(
        json.dumps("Invalid csrf token:" + e.description), 400)
    response.headers['Content-Type'] = 'application/json'
    return response


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
