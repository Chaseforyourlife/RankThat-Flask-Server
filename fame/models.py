from datetime import datetime
from fame import db, login_manager, app
from fame import login_manager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    all_time_matchups_played = db.Column(db.Integer,default=0)
    name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='images/default.jpg')
    password = db.Column(db.String(60), nullable=False)
    date_joined = db.Column(db.String(20), unique=False, nullable=True)
    #posts = db.relationship('Post', backref='author', lazy=True)
    is_admin= db.Column(db.Boolean,nullable=False,default=False)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"



class Noun(db.Model):
    noun_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=False, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,  default='../../../images/default.jpg')
    description = db.Column(db.String(60), nullable=True)
    points = db.Column(db.Float)
    category_name= db.Column(db.String(100),db.ForeignKey('category.name'),nullable=False)

class Category(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='../../../images/default.jpg')
    matchup_count=db.Column(db.Integer,nullable=False,default=0)
    nouns = db.relationship("Noun", backref="category",lazy=True,order_by=Noun.points.desc())
    noun_requests = db.relationship("NounRequest", backref="category",lazy=True)



class CategoryRequest(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='../images/default.jpg')


class NounRequest(db.Model):
    noun_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=False, nullable=False)
    image_file = db.Column(db.String(20), nullable=True)
    description = db.Column(db.String(60), nullable=True)
    category_name= db.Column(db.String(100),db.ForeignKey('category.name'),nullable=False)







#rank_table = db.Table('rank_table',
#    db.Column('person_id',db.Integer, db.ForeignKey('person.person_id')),
#    db.Column('category_id',db.Integer, db.ForeignKey('category.category_id')),
#    db.Column('points',db.Integer)
#)
'''
class Rank(db.Model):
    rank_id=db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Float)
    person_id = db.Column(db.Integer, db.ForeignKey('person.person_id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'))

class Person(db.Model):
    person_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    wiki = db.Column(db.String(60), nullable=True)
    categories = db.relationship('Category', secondary= people_table, backref=db.backref('people_in_category',lazy='dynamic'))

    ranks = db.relationship('Rank',backref='person',lazy=True,order_by=Rank.points.desc())

class Category(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    url_extension = db.Column(db.String(20), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')

    ranks = db.relationship('Rank',backref='category',lazy=True,order_by=Rank.points.desc())
'''
