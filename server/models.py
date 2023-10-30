from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

# necessary for FK constraint upgrades in alembic migrations
metadata = MetaData(naming_convention = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

# creates SQLAlchemy DB ORM
db = SQLAlchemy(metadata = metadata)

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    serialize_rules = ('-user_visited_park.user', )

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, unique = True)
    password = db.Column(db.String)

    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate = db.func.now())

    # relationships
    user_visited_park = db.relationship('UserVisitedPark', back_populates = ('user'))

    # validation
    @validates('username')
    def validates_username(self, key, username):
        if 4 <= len(username) <= 14:
            return username
        else:
            raise ValueError("Username must be between 4 and 14 characters, inclusive!")

class NationalPark(db.Model, SerializerMixin):
    __tablename__ = 'national_parks'

    serialize_rules = ('-user_visited_park.national_park', )

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    state = db.Column(db.String)

    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate = db.func.now())

    # relationships
    user_visited_park = db.relationship('UserVisitedPark', back_populates = ('national_park'))

class UserVisitedPark(db.Model, SerializerMixin):
    __tablename__ = 'user_visited_park'

    serialize_rules = ('-user.user_visited_park', '-national_park.user_visited_park')

    id = db.Column(db.Integer, primary_key = True)
    date_of_visit = db.Column(db.String)

    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    park_id = db.Column(db.Integer, db.ForeignKey('national_parks.id'))

    # relationships
    user = db.relationship('User', back_populates = ('user_visited_park'))
    national_park = db.relationship('NationalPark', back_populates = ('user_visited_park'))