from core import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(32), nullable=False)
    last_name = db.Column(db.String(32), nullable=False)

    def __repr__(self):
        return '<User {firstname} {lastname}>'.format(firstname=self.first_name, lastname=self.last_name)
