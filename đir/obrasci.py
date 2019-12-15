from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed
from đir.modeli import Korisnik
from flask import session

class Registracija(FlaskForm):
    ime = StringField('Korisničko ime', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    lozinka = PasswordField('Lozinka', validators=[DataRequired()])
    potvrda = PasswordField('Potvrda lozinke', validators=[DataRequired(), EqualTo('lozinka')])
    submit = SubmitField('Registriraj se')

    def validate_ime(self, ime):
        korisnik = Korisnik.query.filter_by(ime=ime.data).first()
        if korisnik:
            raise ValidationError('Zauzeto')

    def validate_email(self, email):
        korisnik = Korisnik.query.filter_by(email=email.data).first()
        if korisnik:
            raise ValidationError('Već registriran')

class Uredi(FlaskForm):
    ime = StringField('Korisničko ime', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    avatar = FileField('Slika profila', validators=[FileAllowed(['png', 'jpg', 'heic', 'jpeg'])])
    submit = SubmitField('Uredi')

    def validate_ime(self, ime):
        korisnik = Korisnik.query.filter_by(ime=ime.data).first()
        if korisnik and korisnik.id != session.get("korisnik_id"):
            raise ValidationError('Zauzeto')

    def validate_email(self, email):
        korisnik = Korisnik.query.filter_by(email=email.data).first()
        if korisnik and korisnik.id != session.get("korisnik_id"):
            raise ValidationError('Već registriran')

class Prijava(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    lozinka = PasswordField('Lozinka', validators=[DataRequired()])
    zapamti = BooleanField("Zapamti me")
    submit = SubmitField('Prijavi se')

class ObjavaObrazac(FlaskForm):
    sport = StringField('sport', validators=[DataRequired()])
    opis = TextAreaField('opis', validators=[DataRequired()])
    mjesto = StringField('mjesto', validators=[DataRequired()])
    datum = StringField('datum', validators=[DataRequired()])
    submit = SubmitField('Kreiraj')