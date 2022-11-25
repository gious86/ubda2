from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import *
from . import db
import json


views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)


@views.route('/personnel')
@login_required
def personnel():
    return render_template("personnel.html", user=current_user)


@views.route('/add_person', methods=['GET', 'POST'])
@login_required
def add_person():
    if request.method == 'POST':
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        pin = request.form.get('pin')
        email = request.form.get('email')
        access_level = request.form.get('access_level')
        person = Person.query.filter_by(pin=pin).first()
        if person:
            flash('Pin already exists.', category='error')
        elif len(pin) < 4:
            flash('Too short pin', category='error')
        elif len(first_name) < 1:
            flash('Too short first name', category='error')
        else:
            new_person = Person(first_name=first_name, 
                                    last_name = last_name, 
                                    email = email,
                                    pin = pin,
                                    access_level = access_level,
                                    created_by = current_user.id)
            db.session.add(new_person)
            db.session.commit()
            flash('Person added!', category='success') 
            #return redirect(url_for('views.personnel')) 
    accessLevels = Access_level.query.all()
    return render_template("add_person.html", user=current_user, access_levels = accessLevels)


@views.route('/edit_person/<string:id>', methods=['GET', 'POST'])
@login_required
def edit_person(id):
    person = Person.query.filter_by(id=id).first()
    if not person :
        flash(f'No person with id:{id}', category='error')
        return redirect(url_for('views.personnel'))
    if request.method == 'POST':
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        pin = request.form.get('pin')
        email = request.form.get('email')
        access_level_id = request.form.get('access_level')
        person.first_name = first_name
        person.last_name = last_name
        person.email = email
        person.pin = pin
        person.created_by = current_user.id
        person.access_level = access_level_id
        db.session.add(person)
        db.session.commit()
        flash('Person information updated', category='success')
        return redirect(url_for('views.personnel'))
    accessLevels = Access_level.query.all() 
    return render_template("edit_person.html", user = current_user, 
                                                person = person, 
                                                access_levels = accessLevels)


@views.route('/delete_person/<string:id>', methods=['GET', 'POST'])
@login_required
def delete_person(id):
    person = Person.query.filter_by(id=id).first()
    if not person :
        flash(f'No person with id:{id}', category='error')
        return redirect(url_for('views.personnel'))

    if request.method == 'POST':
        db.session.delete(person)
        db.session.commit()
        flash('Person deleted', category='success')
        return redirect(url_for('views.personnel'))
    return render_template("delete_person.html", user = current_user, person=person)
    

@views.route('/devices')
@login_required
def devices():
    devs = Device.query.all()
    return render_template("devices.html", user = current_user, devs = devs)


@views.route('/edit_device/<string:id>', methods=['GET', 'POST'])
@login_required
def edit_device(id):
    device = Device.query.filter_by(id=id).first()
    if not device :
        flash(f'No device with id:{id}', category='error')
        return redirect(url_for('views.devices'))
    if request.method == 'POST':
        name = request.form.get('Name')
        device.name = name
        db.session.add(device)
        db.session.commit()
        flash('Person information updated', category='success')
        return redirect(url_for('views.devices'))
    return render_template("edit_device.html", user = current_user, device = device)


@views.route('/access_levels')
@login_required
def access_levels():
    accessLevels = Access_level.query.all() 
    return render_template("access_levels.html", user = current_user, access_levels = accessLevels)


@views.route('/add_access_level', methods=['GET', 'POST'])
@login_required
def add_access_level():
    devices = Device.query.all()
    if request.method == 'POST':
        description = request.form.get('description')
        name = request.form.get('name')    
        access_level = Access_level.query.filter_by(name=name).first()
        if access_level:
            flash(f'Access level with name:"{name}" already exists', category='error')
        elif len(name) < 2:
            flash('Too short name', category='error')
        else:
            new_access_level = Access_level(description = description, name = name)
            for device in devices:
                if request.form.get(device.mac):
                    new_access_level.devices.append(device)
            db.session.add(new_access_level)
            db.session.commit()
            flash('Access level added!', category='success') 
            #return redirect(url_for('views.personnel')) 
    devices = Device.query.all()
    return render_template("add_access_level.html", user = current_user, devices = devices)


@views.route('/edit_access_level/<string:id>', methods=['GET', 'POST'])
@login_required
def edit_access_level(id):
    access_level = Access_level.query.filter_by(id=id).first()
    if not access_level :
        flash(f'No Access level with id:{id}', category='error')
        return redirect(url_for('views.access_levels'))
    if request.method == 'POST':
        description = request.form.get('description')
        access_level.description = description
        db.session.add(access_level)
        db.session.commit()
        flash('Access level updated', category='success')
        return redirect(url_for('views.access_levels'))
    devs = Device.query.all()
    return render_template("edit_access_level.html", user = current_user, devs=devs)


@views.route('/delete_access_level/<string:id>', methods=['GET', 'POST'])
@login_required
def delete_access_level(id):
    access_level = Access_level.query.filter_by(id=id).first()
    if not access_level :
        flash(f'No access level with id:{id}', category='error')
        return redirect(url_for('views.access_levels'))
    if request.method == 'POST':
        db.session.delete(access_level)
        db.session.commit()
        flash('Access level deleted', category='success')
        return redirect(url_for('views.access_levels'))
    return render_template("delete_access_level.html", user = current_user, access_level=access_level)