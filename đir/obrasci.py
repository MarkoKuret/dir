from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed
from đir.modeli import Korisnik
from flask import session

#obrazac za registraciju
class Registracija(FlaskForm):
    ime = StringField('Korisničko ime', validators=[DataRequired(), Length(min=3, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    lozinka = PasswordField('Lozinka', validators=[DataRequired()])
    potvrda = PasswordField('Potvrda lozinke', validators=[DataRequired(), EqualTo('lozinka')])
    submit = SubmitField('Registriraj se')

    #provjera jedinstvenosti korisnickog imena
    def validate_ime(self, ime):
        korisnik = Korisnik.query.filter_by(ime=ime.data).first()
        if korisnik:
            raise ValidationError('Zauzeto')

    #provjera jedinstvenosti email-a
    def validate_email(self, email):
        korisnik = Korisnik.query.filter_by(email=email.data).first()
        if korisnik:
            raise ValidationError('Već registriran')

#obrazac za prijavu
class Prijava(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    lozinka = PasswordField('Lozinka', validators=[DataRequired()])
    submit = SubmitField('Prijavi se')


#obrazac za urediti podatke korisnika
class Uredi(FlaskForm):
    ime = StringField('Korisničko ime', validators=[DataRequired(), Length(min=3, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
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


#za novu objavu ili promijenu podataka objave
class ObjavaObrazac(FlaskForm):
    sport = StringField('sport', validators=[DataRequired()])
    opis = TextAreaField('opis', validators=[DataRequired()])
    mjesto = StringField('mjesto', validators=[DataRequired()])
    datum = StringField('datum', validators=[DataRequired()])
    submit = SubmitField('Kreiraj')

#email za reset lozinke
class Zaboravljena_lozinka(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Potvrdi email')

    #dali je email registriran
    def validate_email(self, email):
        korisnik = Korisnik.query.filter_by(email=email.data).first()
        if korisnik is None:
            raise ValidationError('Email nije registriran')

#reset lozinke
class Nova_lozinka(FlaskForm):
    lozinka = PasswordField('Lozinka', validators=[DataRequired()])
    potvrda = PasswordField('Potvrda lozinke', validators=[DataRequired(), EqualTo('lozinka')])
    submit = SubmitField('Potvrdi novu lozinku')

#filter događaja (objava)
class Filter(FlaskForm):
    f_sport = StringField('sport')
    f_mjesto = StringField('mjesto')
    f_submit = SubmitField('Traži')