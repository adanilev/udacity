from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import make_response, flash, abort
from flask import session as login_session
from database_setup import User, Category, Item
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import re
import category
import item
import decorators as decs

app = Flask(__name__)


# HANDLERS
@app.route('/')
def category_list_handler():
    return render_template('category_list.html',
                           categories=category.get_all_categories())


@app.route('/catalogue/<category_name>')
@decs.category_name_exists
def items_in_category_handler(category_name):
    cat = category.get_category(name=category_name)
    items = item.get_items_in_category(cat.id)
    return render_template('items_in_category.html',
                            category_name=category_name, items=items)


@app.route('/catalogue/<category_name>/<item_title>')
@decs.category_name_exists
def item_handler(category_name, item_title):
    # TODO: build the item page
    return render_template('item.html')


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
