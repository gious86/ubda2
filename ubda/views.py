from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Person, Device
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
        pass_code = request.form.get('passCode')
        email = request.form.get('email')
        person = Person.query.filter_by(pass_code=pass_code).first()
        if person:
            flash('Pin already exists.', category='error')
        elif len(pass_code) < 4:
            flash('Too short pin', category='error')
        elif len(first_name) < 1:
            flash('Too short first name', category='error')
        else:
            new_person = Person(first_name=first_name, 
                                    last_name = last_name, 
                                    email = email,
                                    pass_code = pass_code,
                                    created_by=current_user.id)
            db.session.add(new_person)
            db.session.commit()
            flash('Person added!', category='success') 
            #return redirect(url_for('views.personnel')) 
    return render_template("add_person.html", user=current_user)


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
        pass_code = request.form.get('passCode')
        email = request.form.get('email')
        person.first_name = first_name
        person.last_name = last_name
        person.email = email
        person.pass_code = pass_code
        person.created_by = current_user.id
        db.session.add(person)
        db.session.commit()
        flash('Person information updated', category='success')
        return redirect(url_for('views.personnel'))
    return render_template("edit_person.html", user=current_user, person=person)


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
    return render_template("delete_person.html", user=current_user, person=person)
    

@views.route('/devices')
@login_required
def devices():
    devs = Device.query.all()
    return render_template("devices.html", user=current_user, devs = devs)