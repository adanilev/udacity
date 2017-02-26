import sys

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Restaurant(Base):
    """Defines the restaurant table as an object"""
    # define the name of the table
    __tablename__ = 'restaurant'

    # Create a col called name which will contain strings with a max length
    # of 80 chars and may not be null
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)

class MenuItem(Base):
    # define the name of the table
    __tablename__ = 'menu_item'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)

    @property
    def serialize(self):
        return {
            'name'          : self.name,
            'description'   : self.description,
            'id'            : self.id,
            'price'         : self.price,
            'course'        : self.course,
        }


### keep at end ###
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.create_all(engine)
