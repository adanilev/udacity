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
    def wrapper(category_name, item_title, *args, **kwargs):
        itm = item.get_item(title=item_title, category_name=category_name)
        if itm:
            return function(category_name, item_title, *args, **kwargs)
        else:
            abort(404)
            return
    return wrapper
