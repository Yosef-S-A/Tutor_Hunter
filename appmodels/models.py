#!/usr/bin/python3
"""
A class representation of database tables
"""
from datetime import datetime
from appmodels import db, login_manager, app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

class User(db.Model, UserMixin):
    """
    A class representation of The common attributes of tutors & non-tutors
    """
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), unique=False, nullable=False)
    last_name = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(60), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    user_type = db.Column(db.String(6), nullable=False)
    requests = db.relationship('Parent_requests', backref='request_from', lazy=True)
    __mapper_args__ = {
        'polymorphic_identity':'Parent',
        'polymorphic_on':user_type
        }
     
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
        return f"User('{self.first_name}', '{self.email}')"

class Tutor(User, db.Model):
    """
    A class representation of tutors and it inherits form User class
    """
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    rate = db.Column(db.Float, nullable=False)
    header =  db.Column(db.String(120), nullable=False)
    bio =  db.Column(db.String(2000), nullable=False)
    placesofresidence = db.Column(db.String(30), nullable=False)
    image_file = db.Column(db.String(120), nullable=False, default='default.jpg')
    requested = db.relationship('Parent_requests', foreign_keys='Parent_requests.t_id', backref='request_to', lazy=True)
    last_message_read_time = db.Column(db.DateTime)
    lang = db.Column(db.String(120), nullable=False)
    __mapper_args__ = {
        'polymorphic_identity':'Tutor',
    }

    def __repr__(self):
        return f"User('{self.first_name}', '{self.email}', '{self.image_file}')"
      
    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Parent_requests.query.filter_by(request_to=self).filter(
            Parent_requests.date_requested > last_read_time).count()
        
class Parent_requests(db.Model):
    """
    A class representation of the database table that stores requests by potential client
    """
    id = db.Column(db.Integer, primary_key=True)
    t_id = db.Column(db.Integer, db.ForeignKey('tutor.id'), nullable=False)
    p_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_requested = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(12))

    def __repr__(self):
        return f"User('{self.id}', '{self.t_id}', '{self.p_id}', '{self.date_requested}')"
