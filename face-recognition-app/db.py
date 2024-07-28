from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, func, or_, and_, CheckConstraint, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from flask_login import UserMixin
from contextlib import contextmanager
from datetime import datetime

DATABASE_URL = "sqlite:///admin.db"
Base = declarative_base()

class User(Base, UserMixin):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String, index=True)
    employees = relationship('Employee', back_populates='controller')

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String,  nullable=False)
    lastname = Column(String, nullable=False)
    image_path = Column(String,unique=True, nullable=False)
    controller_id = Column(Integer, ForeignKey('admins.id'))
    image_encoding = Column(String, nullable=False)
    controller = relationship('User', back_populates='employees')
    attendances = relationship('Attendance', backref='user', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'controller_id': self.controller_id,
            'image_path': self.image_path 
        }

class Attendance(Base):
    __tablename__ = 'attendance'

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
def init_db():
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def add_user(db, username, password):
    # Cases when the same username is used
    db_user = User(username=username, password=password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def add_employee(db, firstname, lastname,image_path, image_encoding, controller_id):
    db_employee = Employee(firstname=firstname, lastname=lastname, image_path=image_path, image_encoding=image_encoding, controller_id=controller_id)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def get_user(db, username):
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db, id):
    return db.query(User).filter(User.id == id).first()

def get_all_employees(db, ctr_id):
    return db.query(Employee).filter(Employee.controller_id == ctr_id).all()

def get_employee_by_id(db, id):
    return db.query(Employee).filter(Employee.id == id).first()

def delete_employee(db, id):
    emp = db.query(Employee).filter(Employee.id == id).first()
    db.delete(emp)
    db.commit()
    db.close()
    return emp

def get_employee(db, firstname, lastname, controller_id): 
    return db.query(Employee).filter(func.lower(Employee.firstname) == firstname.lower() and
                                     func.lower(Employee.lastname) == lastname.lower()  and 
                                     Employee.controller_id == controller_id).all()

def get_employee_one_name(db, name, controller_id):
    return db.query(Employee).filter(or_(Employee.firstname.ilike(f'%{name.lower()}%') , 
                                     Employee.lastname.ilike( f'%{name.lower()}%') &
                                     Employee.controller_id == controller_id)).all()
    
def edit_employee_image(db, id, firstname, lastname, image_path, image_encoding):
    emp = db.query(Employee).filter(Employee.id == id).first()
    if emp:
        emp.firstname = firstname
        emp.lastname = lastname
        emp.image_path = image_path
        emp.image_encoding = image_encoding
        db.commit()
        return "Success"
    else:
        return "Failure"
    
def edit_employee_no_image(db, id, firstname, lastname):
    emp = db.query(Employee).filter(Employee.id == id).first()
    if emp:
        emp.firstname = firstname
        emp.lastname = lastname
        db.commit()
        return "Success"
    else:
        return "Failure"
    
def add_day(db):
    att = db.query(Attendance).first()
    att.value = att.value + 1
    db.commit()
    return "Success"

def employee_present(db, employee_id):
    att = Attendance(timestamp = datetime.now(), employee_id=employee_id)
    db.add(att)
    db.commit()
    db.refresh(att)
    return att

def get_employee_attendances(db, employee_id):
    return db.query(Attendance).filter(Attendance.employee_id == employee_id).all()