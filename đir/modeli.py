from đir import db, app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

spojka = db.Table("spojka", 
    db.Column("korisnik_id", db.Integer, db.ForeignKey('korisnik.id')),
    db.Column("objava_id", db.Integer, db.ForeignKey('objava.id'))
)


class Korisnik(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ime = db.Column(db.String(20), unique=True, nullable=False)
    email =  db.Column(db.String(120), unique=True, nullable=False)
    lozinka = db.Column(db.Text, nullable=False)
    avatar = db.Column(db.String(20), nullable=False, default='avatar.svg')
    eobv = db.Column(db.Boolean, default=True, nullable=False)
    objave = db.relationship("Objava", backref="admin", lazy=True)
    sudionik = db.relationship("Objava", secondary="spojka", backref="sudionici", lazy=True)

    def nabavi_token(self, trajanje=2000):
        t = Serializer(app.config['SECRET_KEY'], trajanje)
        return t.dumps({'korisnik_id': self.id}).decode('utf-8')

    @staticmethod
    def potvrdi_token(token):
        t = Serializer(app.config['SECRET_KEY'])
        try:
            korisnik_id = t.loads(token)['korisnik_id']
        except:
            return None
        
        return Korisnik.query.get(korisnik_id)

    def __repr__(self):
        return f"Korisnik('{self.ime}', '{self.email}')"


class Objava(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sport = db.Column(db.String(20), nullable=False)
    mjesto = db.Column(db.String(20), nullable=False)
    datum = db.Column(db.DateTime, nullable=False)
    opis = db.Column(db.Text, nullable=False)
    korisnik_id = db.Column(db.Integer, db.ForeignKey('korisnik.id'), nullable=False)
    poruke = db.relationship('Poruka', backref="objava", lazy=True)

    def __repr__(self):
        return f"Korisnik('{self.sport}', '{self.mjesto}')"

class Poruka(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tekst = db.Column(db.String(177), nullable=False)
    ime = db.Column(db.String(20), nullable=False)
    objava_id = db.Column(db.Integer, db.ForeignKey('objava.id'), nullable=False)
