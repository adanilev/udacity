from flask import Flask, request, redirect, jsonify, url_for
from flask import render_template as flask_render_template
from flask import make_response, flash, abort
from flask import session as login_session
from functools import wraps
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import requests
import httplib2
import json
import random
import string
import category
import item
import user
import decorators as decs

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalogue Application"


# Convenience render function
def render_template(*args, **kwargs):
    # pass state to every template in case the user logs in on that page
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # TODO: refresh token here
    # pass user id if logged in, else set to false
    logged_in = 'user_id' in login_session
    if logged_in:
        logged_in = login_session['user_id']
    return flask_render_template(logged_in=logged_in,
                                 STATE=state,
                                 *args, **kwargs)


####################################
# DECORATORS
####################################
def check_logged_in(function):
    """Only use this for handlers where the user is trying to access a URL they
       shouldn't because they will get redirected to the first page with no
       warning if they aren't logged in"""
    @wraps(function)
    def wrapper(*args, **kwargs):
        if 'username' in login_session:
            return function(*args, **kwargs)
        else:
            return redirect(url_for('category_list_handler'))
    return wrapper


def check_owns_item(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        itm = item.get_item(category_name=kwargs['category_name'],
                            title=kwargs['item_title'])

        if itm.owner_id == login_session['user_id']:
            return function(*args, **kwargs)
        else:
            return redirect(url_for('category_list_handler'))
    return wrapper


####################################
# HANDLERS
####################################
@app.route('/test')
def test():
        return render_template('test.html')


@app.route('/')
def category_list_handler():
    return render_template('category_list.html',
                           categories=category.get_all_categories())


@app.route('/category/add', methods=['GET', 'POST'])
@check_logged_in
def add_category_handler():
    if request.method == 'POST':
        new_cat_name = request.form['new-cat-name']
        new_cat_id = category.create_category(new_cat_name)
        if new_cat_id:
            return redirect(url_for('category_list_handler'))
        else:
            error = 'Sorry, that category already exists!'
            return render_template('add_category.html', error=error)
    else:
        return render_template('add_category.html', error='')


@app.route('/catalogue/<category_name>')
@decs.category_name_exists
def items_in_category_handler(category_name):
    cat = category.get_category(name=category_name)
    items = item.get_items_in_category(cat.id)
    return render_template('items_in_category.html',
                           category_name=category_name, items=items)


@app.route('/catalogue/<category_name>/<item_title>')
@decs.category_name_exists
@decs.item_title_exists
def item_handler(category_name, item_title):
    # Have to jump through more hoops because we're not using IDs in the URL
    cat = category.get_category(name=category_name)
    the_item = item.get_item(title=item_title, category_id=cat.id)
    return render_template('item.html', item=the_item, category=cat)


@app.route('/item/add/<category_name>', methods=['GET', 'POST'])
@check_logged_in
@decs.category_name_exists
def add_item_handler(category_name, new_item_title='', new_item_desc=''):
    if request.method == 'POST':
        new_item_title = request.form['new-item-title']
        new_item_desc = request.form['new-item-desc']
        new_item_cat = request.form['new-item-cat']
        new_item_id = item.create_item(title=new_item_title,
                                       description=new_item_desc,
                                       category_id=new_item_cat,
                                       owner_id=login_session['user_id'])

        # If it didn't get created, it's because that name already exists,
        # or they posted something invalid and skipped the FE validation
        if new_item_id:
            return redirect(url_for(
                'item_handler',
                category_name=category_name,
                item_title=new_item_title))
        else:
            error = 'Sorry, an item called %s in %s already exists. Please '\
                    'try entering a different title.' % (new_item_title,
                                                         category_name)
            return render_template('add_item.html',
                                   all_cats=category.get_all_categories(),
                                   category_name=category_name,
                                   error=error,
                                   new_item_title=new_item_title,
                                   new_item_desc=new_item_desc)
    elif request.method == 'GET':
        return render_template('add_item.html',
                               all_cats=category.get_all_categories(),
                               category_name=category_name,
                               error='',
                               new_item_title=new_item_title,
                               new_item_desc=new_item_desc)


@app.route('/item/edit/<category_name>/<item_title>', methods=['GET', 'POST'])
@check_logged_in
@decs.category_name_exists
@check_owns_item
def edit_item_handler(category_name, item_title,
                      new_item_title='', new_item_desc=''):
    # What are we going to change?
    item_to_edit = item.get_item(title=item_title,
                                 category_name=category_name)

    # TODO: get this working via the decorator
    if not item_to_edit:
        return abort(404)

    if request.method == 'POST':
        new_item_title = request.form['new-item-title']
        new_item_desc = request.form['new-item-desc']
        new_item_cat = request.form['new-item-cat']

        edited_item_id = item.update_item(id=item_to_edit.id,
                                          title=new_item_title,
                                          description=new_item_desc,
                                          category_id=new_item_cat)

        # If it didn't get updated, it's because that name already exists,
        # or they posted something invalid and skipped the FE validation
        if edited_item_id:
            return redirect(url_for(
                'item_handler',
                category_name=category.get_category(id=new_item_cat).name,
                item_title=new_item_title))
        else:
            error = 'Sorry, an item called %s in %s already exists. Please '\
                    'try entering a different title.' % (new_item_title,
                                                         category_name)
            return render_template('add_item.html',
                                   all_cats=category.get_all_categories(),
                                   category_name=category_name,
                                   new_item_title=new_item_title,
                                   new_item_desc=new_item_desc,
                                   error=error)
    elif request.method == 'GET':
        return render_template('add_item.html',
                               all_cats=category.get_all_categories(),
                               category_name=category_name,
                               new_item_title=item_to_edit.title,
                               new_item_desc=item_to_edit.description,
                               error='')


@app.route('/item/delete/<category_name>/<item_title>')
@check_logged_in
@decs.category_name_exists
@check_owns_item
def delete_item_handler(category_name, item_title):
    # What are we going to change?
    item_to_delete = item.get_item(title=item_title,
                                   category_name=category_name)

    # TODO: get this working via the decorator
    if not item_to_delete:
        return abort(404)

    item.delete_item(item_to_delete.id)
    return redirect(url_for(
        'items_in_category_handler',
        category_name=category_name))


@app.route('/rest/catalogue')
def rest_get_catalogue_handler():
    """Returns JSON of the whole catalogue"""
    cats = category.get_all_categories()
    items = item.get_all_items()
    result = {}
    result['categories'] = [c.serialize for c in cats]
    result['items'] = [i.serialize for i in items]
    return jsonify(result)


####################################
# AUTH FUNCTIONS
####################################
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

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token

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

    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = user.get_user_id(data["email"])
    if not user_id:
        user_id = user.create_user(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += 'Welcome, '
    output += login_session['username']
    output += '!'
    return output


# Disconnect user's login
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        # Only disconnect a connected user.
        access_token = login_session.get('access_token')
        if access_token is None:
            response = make_response(
                json.dumps('Current user not connected.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
               % access_token)
        h = httplib2.Http()
        result_header, result_content = h.request(url, 'GET')
        result_content = json.loads(result_content)
        # Log them out if the token is no longer valid
        if (result_header['status'] != '200' and
                result_content['error'] != 'invalid_token'):
            # For whatever reason, the given token was invalid.
            response = make_response(
                json.dumps('Failed to revoke token for given user.'), 400)
            response.headers['Content-Type'] = 'application/json'
            return response

        del login_session['gplus_id']
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        return redirect(url_for('category_list_handler'))
    else:
        return redirect(url_for('category_list_handler'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
