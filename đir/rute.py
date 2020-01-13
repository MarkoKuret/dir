from flask import render_template, request, session, flash, redirect, url_for, jsonify
from đir import app, db
from đir.modeli import Korisnik, Objava, Poruka
from đir.obrasci import Registracija, Prijava, ObjavaObrazac, Uredi
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from datetime import datetime, date, timedelta
from PIL import Image, ExifTags
import pusher
import os

pusher_client = pusher.Pusher(
  app_id='930370',
  key='43251c740e8c7fdc4747',
  secret='6cc68633eec00ebf9b9d',
  cluster='eu',
  ssl=True
)



@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


def potrebna_prijava(f):
    @wraps(f)
    def dekorator(*args, **kwargs):
        if session.get("korisnik_id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return dekorator



def spremi(slika, korisnik, stari_avatar):    
    ime, tip = os.path.splitext(slika.filename)
    avatar = korisnik + tip
    datoteka = os.path.join(app.root_path, 'static/avatari', avatar)

    rez = (150, 150)
    slika = Image.open(slika)
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                break
        exif=dict(slika._getexif().items())

        if exif[orientation] == 3:
            slika=slika.rotate(180, expand=True)
        elif exif[orientation] == 6:
            slika=slika.rotate(270, expand=True)
        elif exif[orientation] == 8:
            slika=slika.rotate(90, expand=True)
    except:
        pass
    
    if stari_avatar != "avatar.svg":
        stara_datoteka = os.path.join(app.root_path, 'static/avatari', stari_avatar)
        os.remove(stara_datoteka)

    slika.thumbnail(rez)
    slika.save(datoteka)

    return avatar

def selektiraj():
    dat = (date.today() - timedelta(hours=1))
    objave = Objava.query.filter(Objava.datum >= dat).order_by(Objava.datum).all()
    return objave

@app.route("/", methods=["GET"])
def index():
    if session.get("korisnik_id"):
        return redirect("/objave")
    return render_template("index.html")


@app.route("/postavke", methods=["GET", "POST"])
@potrebna_prijava
def postavke():
    obrazac = Uredi()
    korisnik = Korisnik.query.get(session.get("korisnik_id")) 
    if obrazac.validate_on_submit():
        if obrazac.avatar.data:
            avatar = spremi(obrazac.avatar.data, obrazac.ime.data, korisnik.avatar)
            korisnik.avatar = avatar
        korisnik.ime = obrazac.ime.data
        korisnik.email = obrazac.email.data        
        db.session.commit()
        flash('Ažurirano', 'dobro')
    if request.method == 'GET':
        obrazac.ime.data = korisnik.ime
        obrazac.email.data = korisnik.email
    return render_template("postavke.html", korisnik=korisnik, obrazac=obrazac)

@app.route("/korisnik/<int:id>")
@potrebna_prijava
def korisnik(id):
    korisnik = Korisnik.query.get(id)
    return render_template("korisnik.html", korisnik=korisnik)


@app.route("/objave", methods=["GET", "POST"])
@potrebna_prijava
def objave():
    obrazac = ObjavaObrazac()
    if obrazac.validate_on_submit():
        datum = datetime.strptime(obrazac.datum.data, "%Y/%m/%d %H:%M")
        objava = Objava(sport=obrazac.sport.data, mjesto=obrazac.mjesto.data, datum=datum, opis=obrazac.opis.data, korisnik_id=session["korisnik_id"])
        db.session.add(objava)
        db.session.commit()
        flash('Kreirano', 'dobro')
        return redirect(url_for('objave'))
        #return  render_template("objave.html", obrazac=obrazac, objave=objave)

    objave = selektiraj()
    avatar = Korisnik.query.get(session.get("korisnik_id")).avatar
    return render_template("objave.html", obrazac=obrazac, objave=objave, naslov="Novi događaj", avatar=avatar)

@app.route("/objave/<int:id>", methods=["GET", "POST"])
@potrebna_prijava
def objava(id):
    obrazac = ObjavaObrazac()
    objava = Objava.query.get(id)
    poruke = Poruka.query.filter_by(objava_id=id)
    
    if obrazac.validate_on_submit():
        objava.sport = obrazac.sport.data
        objava.mjesto = obrazac.mjesto.data
        objava.datum = datetime.strptime(obrazac.datum.data, "%Y/%m/%d %H:%M")
        objava.opis = obrazac.opis.data
        db.session.commit()
        flash('Ažurirano', 'dobro')
    if request.method == 'GET':
        obrazac.sport.data = objava.sport
        obrazac.mjesto.data = objava.mjesto
        obrazac.datum.data = objava.datum
        obrazac.opis.data = objava.opis
    return render_template('objava.html', poruke=poruke, objava=objava, obrazac=obrazac, naslov="Uredi", korisnik=Korisnik.query.get(session.get("korisnik_id")))


@app.route('/poruka', methods=['POST'])
@potrebna_prijava
def poruka():

    try:

        ime = request.form.get('ime')
        poruka = request.form.get('poruka')
        id = request.form.get('id')

        nova_poruka = Poruka(tekst=poruka, ime=ime, objava_id=id)
        db.session.add(nova_poruka)
        db.session.commit()

        pusher_client.trigger('poruka-kanal'+id, 'nova-poruka', {'poruka': poruka, 'ime': ime})

        return jsonify({'result' : 'success'})
    
    except:

        return jsonify({'result' : 'failure'})

    return ''

@app.route("/sudionik/<int:id>/<int:status>")
@potrebna_prijava
def sudionik(id, status):
    objava = Objava.query.get(id)
    korisnik = Korisnik.query.get(session.get("korisnik_id"))
    if status == 0:
        objava.sudionici.remove(korisnik)
    else: 
        objava.sudionici.append(korisnik)
    db.session.commit()
    return redirect(request.referrer)

@app.route("/izbriši/<int:id>")
@potrebna_prijava
def izbriši(id):
    objava = Objava.query.get(id)
    poruke = Poruka.query.filter_by(objava_id=id).all()
    if objava.admin.id == session.get("korisnik_id"):
        for poruka in poruke:
            db.session.delete(poruka)
        db.session.delete(objava)

        db.session.commit()
        flash("Objava izbrisana", "dobro")

    return redirect("/")


@app.route("/registracija", methods=["GET", "POST"])
def registracija():

    #session.clear()

    obrazac = Registracija()
    if obrazac.validate_on_submit():
        hash = generate_password_hash(obrazac.lozinka.data)
        korisnik = Korisnik(ime=obrazac.ime.data, email=obrazac.email.data, lozinka=hash)
        db.session.add(korisnik)
        db.session.commit()
        session["korisnik_id"] = korisnik.id
        flash('Bok ' + obrazac.ime.data + ', uspiješno ste registrirani', 'dobro')

        return redirect("/objave")
    return render_template('registracija.html', obrazac=obrazac)

@app.route("/prijava", methods=["GET", "POST"])
def prijava():

    #session.clear()

    obrazac = Prijava()
    if obrazac.validate_on_submit():
        korisnik = Korisnik.query.filter_by(email=obrazac.email.data).first()
        if korisnik and check_password_hash(korisnik.lozinka, obrazac.lozinka.data):
            session['korisnik_id'] = korisnik.id
            return redirect("/objave")
        flash("nevažeći email ili lozinka", 'ne_dobro')
    return render_template('prijava.html', obrazac=obrazac)


@app.route("/odjava")
def odjava():

    session.clear()
    return redirect("/")


