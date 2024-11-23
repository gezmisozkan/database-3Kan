# Database models for the website
from sqlalchemy import func
from . import db  #. means from the current package yani website
from flask_login import UserMixin

class Note(db.Model): # Note isimli bir class oluşturuldu ve db.Model classından miras alıyor
    id = db.Column(db.Integer, primary_key=True) # id columnu oluşturuldu
    data = db.Column(db.String(10000)) # data columnu oluşturuldu
    date = db.Column(db.DateTime(timezone = True), default = func.now()) # date columnu oluşturuldu
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # user_id columnu oluşturuldu ve user tablosundan gelen id ile ilişkilendirildi
    # küçük harfle yazılan user.id, User (aşağıdaki sınıf) tablosundan gelen id columnunu temsil eder


class User(db.Model, UserMixin): # UserMixin, Flask-Login kütüphanesinden geliyor
    id = db.Column(db.Integer, primary_key=True) # id columnu oluşturuldu
    email = db.Column(db.String(150), unique=True) # email columnu oluşturuldu
    password = db.Column(db.String()) # password columnu oluşturuldu
    first_name = db.Column(db.String(150)) # first_name columnu oluşturuldu
    notes = db.relationship('Note') # Buradaki de yukardaki sınıfın adı