import sys

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Employee(Base):
    # define the name of the table
    __tablename__ = 'employee'

    name = Column(String(250), nullable = False)
    id = Column(Integer, primary_key = True)

class Address(Base):
    # define the name of the table
    __tablename__ = 'address'

    street = Column(String(80), nullable = False)
    zip = Column(String(5), nullable = False)
    id = Column(Integer, primary_key = True)
    employee_id = Column(Integer, ForeignKey('employee.id'))
    employee = relationship(Employee)


### keep at end ###
engine = create_engine('sqlite:///employeeData.db')
Base.metadata.create_all(engine)
