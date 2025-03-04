import os
import psycopg2
from dotenv import dotenv_values, load_dotenv

from flask import Flask, request, render_template, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect

from .forms import BoletoForm

config = dotenv_values('.env')


app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://config["USER"]:config["PASSWORD"]@config["HOST"]/config["DBNAME"]'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)


csrf = CSRFProtect(app)


@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        form = BoletoForm()
    return render_template('registro.html', form=form, title='Registro')




if __name__ == '__main__':
    app.run(debug=True)