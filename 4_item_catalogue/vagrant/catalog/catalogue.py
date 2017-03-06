#####
# !!! TO DELETE !!!
####



from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

engine = create_engine('sqlite:///itemcatalogue.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

dprint_level = 4

#TMP!!
login_session = {}
login_session['user_id'] = 1


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
            return ''
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


# Item CRUD methods
def create_item(title, description, category_id):
    '''Create an item. Don't allow two items to have same title and category'''
    # Check if Item already exists (same title and category)
    if get_item(title=title, category_id=category_id):
        dprint(1, "create_item failed. Item with title %s and category_id %s already exists" % (title, category_id))
        return ''
    # If not, create it and return id
    new_item = Item(title=title, description=description,
                    category_id=category_id, owner_id=login_session['user_id'])
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
        dprint(3, "Updated Item: id=%s, title=%s, description=%s, category_id=%s" % (item.id, item.title, item.description, item.category_id))
    else:
        dprint(1, "update_category failed. Category does not exist with id=%s" % id)


def delete_item(id):
    item = get_item(id=id)
    if item:
        session.delete(item)
        session.commit()
        dprint(3, 'Deleted Item id=%s, title=%s' % (id, item.title))
    else:
        dprint(1, "delete_item failed. Item does not exist with id=%s" % id)


def add_to_db(an_obj):
    session.add(an_obj)
    session.commit()


def dprint(level, text):
    """Helper to print depending on level passed. dprint_level is:
    1 = Error
    2 = Warning
    3 = Info
    4 = Debug"""
    prefix = ''
    if level == 1:
        prefix = 'ERROR: '
    elif level == 2:
        prefix = 'WARNING: '
    elif level == 3:
        prefix = 'INFO: '
    elif level == 4:
        prefix = 'DEBUG: '

    if level <= dprint_level:
        print prefix + text

test()
