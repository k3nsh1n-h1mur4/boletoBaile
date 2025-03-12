import os
import segno
import psycopg2
import resend
from qrcode import QRCode as qr
from fpdf import FPDF
from dotenv import dotenv_values
from decouple import config
from pathlib import Path

from .pdfGen import FPDF


import flask
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS, cross_origin

from .forms import BoletoForm

pathFile = Path.cwd() / 'boletoBaile'
UPLOAD_FOLDER = pathFile.joinpath('uploads')
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://config["USER"]:config["PASSWORD"]@config["HOST"]:config["PORT"]/config["DBNAME"]'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(16)
app.config['WTF_CSRF_SECRET_KEY'] = os.urandom(16)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1000 * 1000

csrf = CSRFProtect(app)
csrf.init_app(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}}, expose_headers="*")



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def genQr(data: str, name: str):
    qrCode = segno.make_qr(data, version=10, encoding='utf-8') 
    qrCode.save(Path.cwd().joinpath("boleto" + "_" + name + ".png"))
    return qrCode

@app.route('/')
def index():
    return render_template('index.html', title='Boleto Baile')


@app.route('/register', methods=['GET', 'POST'])
@cross_origin()
def register():
    print(UPLOAD_FOLDER)
    form = BoletoForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            app = form.app.data
            apm = form.apm.data
            nombre = form.nombre.data
            matricula = form.matricula.data
            email = form.email.data
            ine = request.files['ine']
            tarjeton = request.files['tarjeton']
            acta_hijo = request.files['acta_hijo']
            files = [ine, tarjeton, acta_hijo]
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(UPLOAD_FOLDER, filename))
                elif len(files) <= 3:
                    return render_template('/http_codes/400.html', title='Error, falta de Archivos')
            conn = psycopg2.connect(user=config('USER'), password=config('PASSWORD'), host=config('HOST'), dbname=config('DBNAME'), port=config('PORT'))
            cur = conn.cursor()
            cur.execute("INSERT INTO boletos(app, apm, nombre, matricula, email) VALUES (%s, %s, %s, %s, %s);", (app.upper(), apm.upper(), nombre.upper(), matricula.upper(), email))
            conn.commit()
            #flash('Registro exitoso, tú Boleto digital será enviado al correo registrado.')
            return redirect(url_for('success'))
        except psycopg2.Error as e:
            raise e
    return render_template('registro.html', form=form, title='Registro')



@app.route('/getRegisters', methods=['GET'])
@cross_origin()
def getRegisters():
    conn = psycopg2.connect(user=config('USER'), password=config('PASSWORD'), host=config('HOST'), dbname=config('DBNAME'), port=config('PORT'))
    cur = conn.cursor()
    cur.execute("SELECT * FROM boletos;")
    rows = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('getRegisters.html', rows=rows, title='Registros')


@app.route('/pdfGen/<int:id>', methods=['GET'])
def qrcode(id):
    id = id
    conn = psycopg2.connect(user=config('USER'), password=config('PASSWORD'), host=config('HOST'), dbname=config('DBNAME'), port=config('PORT'))
    cur = conn.cursor()
    cur.execute("SELECT * FROM boletos WHERE id = %s", (id,))
    rows = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    pdf = FPDF()
    pdf.Image()
    pdf.output("boleto.pdf")
    genQr(str(rows), str(rows[4]))
    return render_template('boleto.html', id=id)


@app.route('/sendMail', methods=['GET', 'POST'])
def sendMail():
    resend.api_key = config('RESEND_API_KEY')
    params: resend.Emails.SendParams = {
        "from": "Acme <onboarding@resend.dev>",
        "to": ["isaac.acervantes@gmail.com"],
        "subject": "Boleto Baile",
        "html": f"Hola, tu boleto digital ha sido generado, puedes verlo en <a href='http://localhost:5000/qrcode/{id}'>este enlace</a>",
        "text": "Hola, tu boleto digital ha sido generado, puedes verlo en este enlace http://localhost:5000/qrcode/{id}"
    }
    r = resend.Emails.send(params)
    return jsonify(r)
    
    

@app.route('/error')
def error():
    return render_template('/http_codes/400.html')

@app.route('/success')
def success():
    return render_template('/http_codes/200.html')


if __name__ == '__main__':
    app.run(debug=True)