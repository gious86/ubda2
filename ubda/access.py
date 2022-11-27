from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from .models import Access_level, Person, Device, Output, Access_log
from . import db, sock, hostname, device_models
import qrcode
import io
import json
import time


to_devices = {}

access = Blueprint('access', __name__)


def activate_allowed_outputs(person, device, method):
    log_entry = Access_log(device = device.id, person = person.id)
    access_level = Access_level.query.filter_by(id = person.access_level).first()
    if not device in access_level.devices:
        result = -1
        log_entry.content = "access denied, method: " + method
    else:
        outputs = []
        for o in access_level.outputs:
            if o.device == device.id:
                outputs.append(o.n)
        cmd = '{"open":%s}' %str(outputs)
        to_devices.update({device.id:cmd}) 
        result = 1
        log_entry.content = "access granted, method: " + method
    db.session.add(log_entry)
    db.session.commit()
    return result

@access.route("/qr/<string:id>")
def qr_generator(id):
    url = hostname + url_for('access.qr_access', id = id)
    qr_img = generate_qr(url)
    return send_file(qr_img, mimetype='image/png')


@access.route("/access/<string:id>", methods=['GET', 'POST'])
def qr_access(id):
    device = Device.query.filter_by(mac = id).first()
    if request.method == 'POST':
        pin = request.form.get('pin')
        person = Person.query.filter_by(pin=pin).first()
        if not person:
            flash('Wrong pin')
        elif not device:
            flash(f'device with id:{id} does not exist!')
        elif activate_allowed_outputs(person, device, 'pin') > 0: 
            flash(f'Welcome {person.first_name}')
        else:
            flash(f'Sorry {person.first_name}, you have no access!')
        return render_template('message.html', url = url_for('access.qr_access', id = device.mac))         
    elif device:
        return render_template('qr_access.html')
    else:
        flash(f'device with id:{id} does not exist!')
        return render_template('message.html', url = url_for('views.home'))


def generate_qr(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_io = io.BytesIO()
    img.save(img_io)
    img_io.seek(0)
    return img_io


@sock.route('/ws/<string:id>')
def qr_access(ws, id):
    client_ip = request.remote_addr
    print(f'incomming connection id:"{id}"')
    data = ws.receive(1)
    if not data:
        print('timeout')
        ws.close()
        return
    else:
        model = None        
        try:
            js = json.loads(data)
            model = js['model']
        except Exception as e:              
            print(f'exception:{e}')
        if not model:
            print('unsupported format, closing connection...')
        elif not model in device_models:     
            print(f'unknown device model "{model}", closing connection...')
        else:
            print(f'connection from:"{client_ip}", device id: "{id}", device model: "{model}"')   
            device = Device.query.filter_by(mac=id).first()
            if not device:
                print(f'new device adding to DB...')
                device = Device(mac = id, model = model, last_seen = int(time.time()))
                db.session.add(device)
                db.session.commit()
                n_of_outputs = device_models[model]['outputs']
                for n in range(1, n_of_outputs+1):
                    output = Output(device = device.id, n=n)
                    db.session.add(output)
                db.session.commit()
                print(f'device with id:{id} added to DB')
            else :
                print('known device')
        while True:
            try:
                data = ws.receive(1) 
                if data:
                    print(f'from device "{device.mac}" - "{data}"')
                    device.last_seen = int(time.time())
                    js = ''
                    try:
                        js = json.loads(data)
                    except: pass
                    if js:
                        if 'card' in js:
                            card = js['card']
                            person = Person.query.filter_by(card_number = card).first()
                            if person:
                                if activate_allowed_outputs(person, device, 'card') > 0: 
                                    print(f'access granted - {person.first_name}')
                                else:
                                    print(f'no access - {person.first_name}')
                            else :
                                log_entry = Access_log(device = device.id, 
                                                        content = 'unknown card:' + card)
                                db.session.add(log_entry)
                                db.session.commit()
                                print(f'unknown card:{card}')
                        #if something in js: do something
                    db.session.add(device)
                    db.session.commit()
                if device.id in to_devices:
                    cmd = to_devices[device.id]
                    print(f'to device "{device.mac}" - "{cmd}"')
                    ws.send(cmd)
                    to_devices.pop(device.id)
            except Exception as e:
                print(f'connection with "{id}" closed. e:{e}')
                break