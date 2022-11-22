from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from .models import Access_point, Person
from . import db
from . import hostname
from . import sock
import qrcode
import io
from .models import Device
import json

access = Blueprint('access', __name__)


@access.route("/qr/<string:id>")
def qr_generator(id):
    url = hostname + url_for('access.qr_access', id = id)
    qr_img = generate_qr(url)
    return send_file(qr_img, mimetype='image/png')


@access.route("/access/<string:id>", methods=['GET', 'POST'])
def qr_access(id):
    if request.method == 'POST':
        code = request.form.get('passcode')
        person = Person.query.filter_by(pass_code=code).first()
        if person:
            flash(f'Welcome {person.first_name}')
            return render_template('message.html') #'<h1>Access granted</h1>'
        else:
            flash('Wrong code')
            return render_template('message.html') #'Wrong code'
    else:
        device = Device.query.filter_by(mac = id).first()
        if device:
            return render_template('qr_access.html')
        else:
            flash(f'device with id:{id} does not exist!')
            return render_template('message.html')


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
    data = ws.receive()
    model = None
    try:
        js = json.loads(data)
        model = js['model']
    except Exception as e:
        print(f'exception:{e}') 
    if model:
        print(f'connection from:"{client_ip}", device id: "{id}", model: "{model}"')
    else:
        print('unsupported format')
        return
    device = Device.query.filter_by(mac=id).first()
    if not device:
        print(f'new device adding to DB...')
        device = Device(
                mac = id,
                model = model,
        )
        db.session.add(device)
        db.session.commit()
        print(f'device with id:{id} added to DB')
    else :
        print('known device')
    while True:
        try:
            data = ws.receive()
            print(data)
            ws.send(data)
        except:
            print('connection with "{id}" closed')
            break