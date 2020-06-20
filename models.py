from exits import db
# from flask_sqlalchemy import SQLAlchemy as db
from werkzeug.security import generate_password_hash,check_password_hash
import datetime
class User(db.Model):
    __tablename__='user'
    id=db.Column(db.Integer,autoincrement=True,primary_key=True)
    phone=db.Column(db.String(11),nullable=False)
    username=db.Column(db.String(50),nullable=False)
    password=db.Column(db.String(100),nullable=False)

    def __init__(self,*args,**kwargs):
        phone=kwargs.get('phone')
        username = kwargs.get('username')
        password = kwargs.get('password')

        self.phone=phone
        self.username=username
        self.password=generate_password_hash(password)

    def check(self,old_pwd):
        result=check_password_hash(self.password,old_pwd)
        return result

class Type(db.Model):
    __tablename__='type'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    title=db.Column(db.String(50),nullable=False)
    description=db.Column(db.Text,nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref=db.backref('types'))


class Article(db.Model):
    __tablename__='article'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    title=db.Column(db.String(50),nullable=False)
    content=db.Column(db.Text,nullable=False)
    description=db.Column(db.Text,nullable=False)
    zan_num=db.Column(db.Integer,default=0,nullable=False)
    up_time=db.Column(db.DateTime,default=datetime.datetime.now)

    type_id = db.Column(db.Integer, db.ForeignKey('type.id'))
    type = db.relationship('Type', backref=db.backref('articles',order_by=up_time.desc()))

    author_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    author=db.relationship('User',backref=db.backref('articles'))


class Commten(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    content_time = db.Column(db.DateTime, default=datetime.datetime.now)

    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    article = db.relationship('Article', backref=db.backref('comments', order_by=content_time.desc()))

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref=db.backref('comments'))

class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    content_time = db.Column(db.DateTime, default=datetime.datetime.now)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref=db.backref('messages'))