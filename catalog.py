from flask import Flask, render_template, request, redirect, jsonify, url_for, make_response, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CatalogItem, User
from flask import session as login_session
import random
import string
import requests
from flask_wtf.csrf import CSRFProtect
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
CSRFProtect(app)


######################
# JSON API Section
######################

@app.route('/api/v1/catalog/')
def showCatalogJSON():
    categoryItems = session.query(CatalogItem).order_by(CatalogItem.id.desc())
    return jsonify(Items=[i.serialize for i in categoryItems])
	
@app.route('/api/v1/categories/')
def showCategoryJSON():
    categories = session.query(Category).all()
    return jsonify(Categories=[i.serialize for i in categories])

@app.route('/api/v1/catalog/<int:catalog_id>')
@app.route('/api/v1/catalog/<int:catalog_id>/items')
def detailCategoryJSON(catalog_id):
	categoryItems = session.query(CatalogItem).filter_by(category_id = catalog_id).all()
	return jsonify(Items=[i.serialize for i in categoryItems])

@app.route('/api/v1/catalog/<int:catalog_id>/item/<int:item_id>')
def detailItemJSON(catalog_id, item_id):
	catalogItem = session.query(CatalogItem).filter_by(id = item_id).first()
	return jsonify(Item=catalogItem.serialize)

##################################
# Catalog Read Operation Section
##################################	
	
# Show all categories
@app.route('/')
@app.route('/catalog/')
def showCategory():
	categories = session.query(Category).all()
	categoryItems = session.query(CatalogItem).order_by(CatalogItem.id.desc()).limit(10)
	# return "This page will show all my categories"
	return render_template('index.html', categories=categories, categoryName = 'Latest Items', categoryItems=categoryItems)

@app.route('/catalog/<int:catalog_id>')
@app.route('/catalog/<int:catalog_id>/items')
def detailCategory(catalog_id):
	# Get all categories
	categories = session.query(Category).all()


	category = session.query(Category).filter_by(id = catalog_id).first()
	categoryName = category.name
	categoryId = category.id
	categoryItems = session.query(CatalogItem).filter_by(category_id = catalog_id).all()
	return render_template('index.html', categories = categories, categoryItems = categoryItems, categoryName = categoryName, categoryId = categoryId)

	
@app.route('/catalog/<int:catalog_id>/item/<int:item_id>')
def detailItem(catalog_id, item_id):
	catalogItem = session.query(CatalogItem).filter_by(id = item_id).first()
	creator = getUserInfo(catalogItem.user_id)
	if login_session.get('user_id') == creator.id:
		canEdit = True
	else: canEdit = False
	return render_template('detail_item.html', catalog_id=catalog_id, catalogItem = catalogItem, creator=creator, canEdit=canEdit)

	
##################################
# Catalog Update Operations Section
##################################
@app.route(
    '/catalog/<int:catalog_id>/item/<int:item_id>/edit',
    methods=['GET', 'POST'])
def editItem(catalog_id, item_id):
    if validate_login():
        return redirect(url_for('showLogin'))	
    editedItem = session.query(CatalogItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['image_url']:
            editedItem.image_url = request.form['image_url']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('detailItem', catalog_id=catalog_id, item_id=item_id))
    else:
        return render_template(
            'edit_item.html', catalog_id=catalog_id, item_id=item_id, item=editedItem)

##################################
# Catalog Create Operation Section
##################################
@app.route(
    '/catalog/item/create',
    methods=['GET', 'POST'])
def createItem():
	if validate_login():
		return redirect(url_for('showLogin'))	
	# Get all categories
	categories = session.query(Category).all()
	if request.method == 'POST':
		print 'show --->' + request.form['category']
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
def deleteItem(catalog_id, item_id):
	if validate_login():
		return redirect(url_for('showLogin'))
	itemToDelete = session.query(CatalogItem).filter_by(id=item_id).one()
	if itemToDelete.user_id != login_session.get('user_id'):
		return "<script>function myFunction() {alert('You are not authorized to delete this item. Please create your own item in order to delete.');}</script><body onload='myFunction()''>"
	if request.method == 'POST':
		session.delete(itemToDelete)
		session.commit()
		return redirect(url_for('showCategory'))
	else:
		return render_template('delete_item.html', item=itemToDelete)
    # return "This page is for deleting menu item %s" % menu_id

	
##################################
# Login Handling Section
##################################

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

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
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
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
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    # flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output
	
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
	
def validate_login():
	if 'username' not in login_session:
		return True
	else: return False

##################################
# Disconnect Handling Section
##################################		
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('credentials')
    if access_token is None:
 	print 'Access Token is None'
    	response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['credentials']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] != '200':
		# Error occured, clear session. Otherwise login will be stuck forever
        #login_session.clear()
    	response = make_response(json.dumps('Failed to revoke token for given user.', 401))
    	response.headers['Content-Type'] = 'application/json'
    	return response


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
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
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]


    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    ''' 
        Due to the formatting for the result from the server token exchange we have to 
        split the token first on commas and select the first index which gives us the key : value 
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
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
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
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
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategory'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategory'))
	
if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='0.0.0.0', port=5000)