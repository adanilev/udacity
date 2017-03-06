from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

import utils

dprint = utils.dprint

engine = create_engine('sqlite:///itemcatalogue.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Item CRUD methods
def create_item(title, description, category_id, owner_id):
    '''Create an item. Don't allow two items to have same title and category'''
    # Check if Item already exists (same title and category)
    if get_item(title=title, category_id=category_id):
        dprint(1, "create_item failed. Item with title %s and category_id %s already exists" % (title, category_id))
        return ''
    # If not, create it and return id
    new_item = Item(title=title, description=description,
                    category_id=category_id, owner_id=owner_id)
    add_to_db(new_item)
    dprint(3, "Created Item: id=%s, title=%s, category_id=%s" % (new_item.id, new_item.title, new_item.category_id))
    return new_item.id


def get_item(id='', title='', category_id=''):
    '''Get item by id OR (title AND category_id)'''
    if id:
        # search by id
        if session.query(Item.id).filter_by(id=id).scalar() is None:
            # return None if it doesn't exist
            return ''
        else:
            return session.query(Item).filter_by(id=id).one()
    elif title and category_id:
        # search by name
        if session.query(Item.id).filter_by(title=title, category_id=category_id).scalar() is None:
            # return None if it doesn't exist
            return ''
        else:
            return session.query(Item).filter_by(title=title, category_id=category_id).one()
    else:
        dprint(1, "Insufficient parameters passed to get_item. id=%s, title=%s, category_id=%s" % (id, title, category_id))
        return ''


def get_items_in_category(category_id=''):
    return session.query(Item).filter_by(category_id=category_id).all()


def update_item(id, title='', description='', category_id=''):
    item = get_item(id=id)
    if item:
        # Only update fields that get passed in the params
        if title:
            item.title = title
        if description:
            item.description = description
        if category_id:
            item.category_id = category_id
        # Update it
        add_to_db(item)
        dprint(3, "Updated %s" % item_tostring(item))
    else:
        dprint(1, "update_category failed. \
            Category does not exist with id=%s" % id)


def item_tostring(item):
    return "Item: id=%s, title=%s, description=%s, category_id=%s, "\
           "owner_id=%s" % (str(item.id), item.title, item.description,
           str(item.category_id), str(item.owner_id))


def add_to_db(an_obj):
    session.add(an_obj)
    session.commit()


def delete_item(id):
    item = get_item(id=id)
    if item:
        session.delete(item)
        session.commit()
        dprint(3, 'Deleted Item id=%s, title=%s' % (id, item.title))
    else:
        dprint(1, "delete_item failed. Item does not exist with id=%s" % id)
