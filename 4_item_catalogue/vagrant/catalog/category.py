from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

import utils

dprint = utils.dprint

engine = create_engine('sqlite:///itemcatalogue.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Category CRUD methods
def create_category(name):
    # Check if Category name already exists
    if get_category(name=name):
        dprint(1, "create_category failed. Category name %s already exists" % name)
        return ''
    # If not, create it and return id
    new_cat = Category(name=name)
    add_to_db(new_cat)
    dprint(3, "Created Category: id=%s, name=%s" % (new_cat.id, name))
    return new_cat.id


def get_category(id ='', name=''):
    if id:
        # search by id
        if session.query(Category.id).filter_by(id=id).scalar() is None:
            # return None if it doesn't exist
            return None
        else:
            return session.query(Category).filter_by(id=id).one()
    elif name:
        # search by name
        if session.query(Category.id).filter_by(name=name).scalar() is None:
            # return None if it doesn't exist
            return ''
        else:
            return session.query(Category).filter_by(name=name).one()
    else:
        dprint(1, "Nothing passed to get_category")
        return ''


def get_all_categories():
    return session.query(Category).all()


def update_category(id, name):
    cat = get_category(id=id)
    if cat:
        # If there's a Category with id
        cat.name = name
        add_to_db(cat)
        dprint(3, "Updated Category: id=%s, name=%s" % (id, name))
    else:
        dprint(1, "update_category failed. Category does not exist with id=%s" % id)


def delete_category(id):
    cat = get_category(id=id)
    if cat:
        session.delete(cat)
        session.commit()
        dprint(3, 'Deleted Category id=%s, name=%s' % (id, cat.name))
    else:
        dprint(1, "delete_category failed. Category does not exist with id=%s" % id)


def add_to_db(an_obj):
    session.add(an_obj)
    session.commit()
