from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


accessLevel_device = db.Table('accessLevel_device',
                                  db.Column('device_id', db.Integer, db.ForeignKey('device.id')),
                                  db.Column('access_level_id', db.Integer, db.ForeignKey('access_level.id'))
                                  )

"""
accessLevel_person = db.Table('accessLevel_person',
                                  db.Column('person_id', db.Integer, db.ForeignKey('person.id')),
                                  db.Column('access_level_id', db.Integer, db.ForeignKey('access_level.id'))
                                  )
"""

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    pin = db.Column(db.String(10), unique=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    department = db.Column(db.Integer, db.ForeignKey('department.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    #access_levels = db.relationship('Access_level', secondary=accessLevel_person, back_populates='personnel'
    access_level = db.Column(db.Integer, db.ForeignKey('access_level.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    departments = db.relationship('Department')
    group = db.Column(db.Integer, db.ForeignKey('user_group.id'))
    personnel = db.relationship('Person')

class User_group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    users = db.relationship('User')

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(50))
    manager = db.Column(db.Integer, db.ForeignKey('user.id'))
    personnel = db.relationship('Person')

class Access_point(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    output_device = db.Column(db.Integer, db.ForeignKey('device.id'))
    outpit_no = db.Column(db.Integer)

class Access_level(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(50))
    devices = db.relationship('Device', secondary=accessLevel_device, back_populates='access_levels')
    personnel = db.relationship('Person') #, secondary=accessLevel_person)  #, backref='access_levels')
    

class Time_zone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.Time(timezone=True))
    end = db.Column(db.Time(timezone=True))

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    model = db.Column(db.String(50))
    ip_address = db.Column(db.String(50))
    mac = db.Column(db.String(50))
    is_online = db.Column(db.Integer)
    access_levels = db.relationship('Access_level', secondary=accessLevel_device, back_populates='devices')
