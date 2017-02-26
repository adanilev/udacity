from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Employee, Address

engine = create_engine('sqlite:///employeeData.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

newEmp = Employee(name = "Rebecca Allen")
rebeccaAddress = Address(street = "512 Sycamore Road", zip = "02001", employee = newEmp)
session.add(newEmp)
session.add(rebeccaAddress)
session.commit()

# print all the employees' names
emps = session.query(Employee).all()
for emp in emps:
    print emp.name
