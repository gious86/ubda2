from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from .models import Access_level, Person
from . import db
from . import hostname
from . import sock
import qrcode
import io
from .models import Device
import json

to_devices = {}

access = Blueprint('access', __name__)


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
        else: 
            access_level = Access_level.query.filter_by(id = person.access_level).first()
            if not device in access_level.devices:
                flash(f'Sorry {person.first_name}, you have no access!')
            else:
                to_devices.update({device.id:'{"open":3}'}) 
                flash(f'Welcome {person.first_name}')
        return render_template('message.html', url = url_for('access.qr_access', id = device.mac))         
    else:
        if device:
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
    data = ws.receive(10)
    if not data:
        print('timeout')
        ws.close()
        return
    else:
        model = None
        if len(data) < 100:
            try:
                js = json.loads(data)
                model = js['model']
            except Exception as e:              
                print(f'exception:{e}')
        if not model:
            print('unsupported format, closing connection...')
            ws.close()
            return
        print(f'connection from:"{client_ip}", device id: "{id}", model: "{model}"')   
        device = Device.query.filter_by(mac=id).first()
        if not device:
            print(f'new device adding to DB...')
            device = Device(mac = id, model = model)
            db.session.add(device)
            db.session.commit()
            print(f'device with id:{id} added to DB')
        else :
            print('known device')
    while True:
        try:
            data = ws.receive(1) 
            if data:
                print(f'from device "{device.mac}" - "{data}"')
            #if have something to send:
                #ws.send(something)
            cmd = None
            try:
                cmd = to_devices[device.id]
            except KeyError:
                pass
            if cmd:
                print(f'to device "{device.mac}" - "{cmd}"')
                ws.send(cmd)
                to_devices.pop(device.id)
        except Exception as e:
            print(f'connection with "{id}" closed. e:{e}')
            break