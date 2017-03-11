import random

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item, User

engine = create_engine('sqlite:///itemcatalogue.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Jean-Luc Picard", email="captain@enterprise.com",
             picture='https://pbs.twimg.com/profile_images/588148795512225792/7GylihCL_reasonably_small.jpg')
session.add(User1)
session.commit()

lorem = """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do
        eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
        minim veniam, quis nostrud exercitation ullamco laboris nisi ut
        aliquip ex ea commodo consequat. Duis aute irure dolor in
        reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
        pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
        culpa qui officia deserunt mollit anim id est laborum."""

#categories
for i in range(1, 10):
    cat = Category(name='Category%s' % str(i))
    session.add(cat)
    session.commit()
    #add items to that Category
    for j in range(1,10):
        item = Item(title='Item %s:%s' % (str(i),str(j)), description=lorem,
                    category_id=cat.id, owner_id=User1.id)
        session.add(item)
        session.commit()

print "SUCCESS: db populated"
