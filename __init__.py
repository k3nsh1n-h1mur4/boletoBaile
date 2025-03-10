import os
import psycopg2
from dotenv import dotenv_values
from decouple import config
from pathlib import Path

import flask
from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS, cross_origin

from .forms import BoletoForm

UPLOAD_FOLDER = Path.cwd() / 'uploads'
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
cors = CORS(app, resources={r"/*": {"origins": "*"}})


def allowed_file(filename1, filename2, filename3):
    return '.' in filename1 and filename1.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

       


@app.route('/')
def index():
    return render_template('index.html', title='Boleto Baile')


    


@app.route('/register', methods=['GET', 'POST'])
@cross_origin()
def register():
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
                if file:
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
def getRegisters():
    conn = psycopg2.connect(user=config('USER'), password=config('PASSWORD'), host=config('HOST'), dbname=config('DBNAME'), port=config('PORT'))
    cur = conn.cursor()
    cur.execute("SELECT * FROM boletos;")
    rows = cur.fetchall()
    return render_template('getRegisters.html', rows=rows, title='Registros')


@app.route('/error')
def error():
    return render_template('/http_codes/400.html')

@app.route('/success')
def success():
    return render_template('/http_codes/200.html')


if __name__ == '__main__':
    app.run(debug=True)