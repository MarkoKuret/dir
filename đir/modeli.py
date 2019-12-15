from đir import db

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
    objave = db.relationship("Objava", backref="admin", lazy=True)
    sudionik = db.relationship("Objava", secondary="spojka", backref="sudionici", lazy=True)

    def __repr__(self):
        return f"Korisnik('{self.ime}', '{self.email}')"


class Objava(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sport = db.Column(db.String(20), nullable=False)
    mjesto = db.Column(db.String(20), nullable=False)
    datum = db.Column(db.DateTime, nullable=False)
    opis = db.Column(db.Text, nullable=False)
    korisnik_id = db.Column(db.Integer, db.ForeignKey('korisnik.id'), nullable=False)

    def __repr__(self):
        return f"Korisnik('{self.sport}', '{self.mjesto}')"