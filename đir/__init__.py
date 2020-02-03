from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from tempfile import mkdtemp
import locale
from flask_mail import Mail

# konfiguracije aplikacije
app = Flask(__name__)
app.config["SECRET_KEY"] = "EsV5ClS1GHistLq6"
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] =  'sqlite:///đir.db'
#'postgres://eiejqpoxnoymrt:ab40bdba72afe8e5a8b547bd77debbac639ed8ad0840f55c160667511b24409d@ec2-174-129-255-91.compute-1.amazonaws.com:5432/dft1sn2094ltj8'
db = SQLAlchemy(app)

# konfiguracija sessiona
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = mkdtemp()
Session(app)

#lokalizacija (za datume na hr)
locale.setlocale(locale.LC_ALL, "hr_HR.UTF-8")


#konfiguracija email servera
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'dirmreza@gmail.com'
app.config['MAIL_PASSWORD'] = 'supertajna'
mail = Mail(app)

#import svih ruta (i funkcija)
from đir import rute
