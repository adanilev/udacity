from flask import abort
from functools import wraps
import category, item


# DECORATOR FUNCTIONS
def category_name_exists(function):
    @wraps(function)
    def wrapper(category_name, *args, **kwargs):
        cat = category.get_category(name=category_name)
        if cat:
            return function(category_name, *args, **kwargs)
        else:
            abort(404)
            return
    return wrapper


def item_title_exists(function):
    @wraps(function)
    def wrapper(category_name, item_name):
        cat = category.get_category(name=category_name)
        if cat:
            return function(category_name)
        else:
            abort(404)
            return
    return wrapper
