import base64
import enum
from datetime import datetime, timedelta
from hashlib import md5
import json
import os
from time import time
from flask import current_app, url_for
from flask_login import UserMixin,current_user
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import redis
import rq
from app import db, login
#from app.search import add_to_index, remove_from_index, query_index
from sqlalchemy import and_
from sqlalchemy.orm import column_property

#region ShoppingList

class ShopListRequestStatus(enum.Enum):
    Open = 1
    Completed = 2
    Cancelled = 3


class ShopListRequest(db.Model):
    __tablename__ = 'shop_list_request'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    product_id = db.Column(db.Integer,db.ForeignKey('shop_list_product.id'))
    requestor = db.relationship('User', foreign_keys='ShopListRequest.user_id',
                                back_populates='shop_list_requests')
    product = db.relationship('ShopListProduct',foreign_keys='ShopListRequest.product_id',
                              back_populates='requests')
    requested_datetime = db.Column(db.DateTime,default=datetime.utcnow)
    status = db.Column(db.Enum(ShopListRequestStatus))

    completed_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    completed_datetime = db.Column(db.DateTime)

    def __repr__(self):
        return '<{0} request for {1}>'.format(self.status,self.product.description)


class ShopListProduct(db.Model):
    __tablename__ = 'shop_list_product'
    __searchable__ = ['description']
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(50))
    picture = db.Column(db.LargeBinary)
    barcode = db.Column(db.String(13))
    requests = db.relationship('ShopListRequest',foreign_keys='ShopListRequest.product_id',
                                lazy='dynamic',viewonly=True,
                                back_populates='product')
    open_requests = db.relationship(ShopListRequest,
                                    primaryjoin=and_(ShopListRequest.product_id == id,ShopListRequest.status == ShopListRequestStatus.Open))


    def __repr__(self):
        return '<Product {}>'.format(self.description)
    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'barcode': self.barcode,
        }

    def make_request(self,**kwargs):
        if kwargs.get('user'):
            user = kwargs['user']
        else:
            user = current_user
        r = ShopListRequest(user_id = user,
                            product_id = self.id,
                            requestor = user,
                            status = ShopListRequestStatus.Open)
        db.session.add(r)
        db.session.commit()

#endregion


#region WeatherData
class WeatherData(db.Model):
    __tablename__ = 'mqttlog'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    source_topic = db.Column(db.String(120), index=True)
    data = db.Column(db.String(120))
#endregion

#region User
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    role_admin = db.Column(db.Boolean)

    shop_list_requests = db.relationship('ShopListRequest',
                                        foreign_keys='ShopListRequest.user_id',
                                        lazy='dynamic',
                                        back_populates='requestor')


    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        if not self.email:
            return ''
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'


    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username': self.username,
            'last_seen': self.last_seen.isoformat() + 'Z',
            'about_me': self.about_me,
            '_links': {
                'self': url_for('api.get_user', id=self.id),
                'avatar': self.avatar(128)
            }
        }
        if include_email:
            data['email'] = self.email
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'about_me']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

#endregion