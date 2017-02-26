from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

# Create engine (same as creating the DB?)
engine = create_engine('sqlite:///restaurantmenu.db')
# Link the Base object to the DB
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
# Create a session
session = DBSession()
# Create an object (i.e. a row in the restaurant table)
firstRest = Restaurant(name = "Pizza Palace")
# Add it to our session (staging)
session.add(firstRest)
# Commit the stuff in the session to the DB
session.commit()
# Get the rows of Restaurant (returns an Object)
session.query(Restaurant).all()
