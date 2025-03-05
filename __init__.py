import os
import psycopg2
from dotenv import dotenv_values
from decouple import config
from pathlib import Path


from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect

from .forms import BoletoForm

UPLOAD_FOLDER = Path.cwd() / 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://config["USER"]:config["PASSWORD"]@config["HOST"]/config["DBNAME"]'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(16)
app.config['WTF_CSRF_SECRET_KEY'] = os.urandom(16)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

csrf = CSRFProtect(app)
csrf.init_app(app)


@app.route('/')
def index():
    return render_template('index.html', title='Boleto Baile')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = BoletoForm(request.form)
    if request.method == 'POST' and form.validate():
        app = form.app.data
        apm = form.apm.data
        nombre = form.nombre.data
        matricula = form.matricula.data
        email = form.email.data
        ine = request.files['ine']
        tarjeton = request.files['tarjeton']
        acta_hijo = request.files['acta_hijo']
        print(ine)
        conn = psycopg2.connect(user=config('USER'), password=config('PASSWORD'), host=config('HOST'), dbname=config('DBNAME'), port=config('PORT'))
        cur = conn.cursor()
        cur.execute("INSERT INTO boletos(app, apm, nombre, matricula, email) VALUES (%s, %s, %s, %s, %s);", (app.upper(), apm.upper(), nombre.upper(), matricula.upper(), email))
        conn.commit()
        flash('Registro exitoso')
        return redirect(url_for('index'))
    return render_template('registro.html', form=form, title='Registro')




if __name__ == '__main__':
    app.run(debug=True)