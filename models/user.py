# -*- coding: utf-8 -*-
from flask_login import UserMixin as LoginUserMixin
from core.access import UserMixin as RbacUserMixin
from core import db, rbac

users_roles = db.Table(
    'users_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class User(db.Model, LoginUserMixin, RbacUserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    # Other columns
    roles = db.relationship(
        'Role',
        secondary=users_roles,
        backref=db.backref('roles', lazy='dynamic')
    )

    def add_role(self, role):
        self.roles.append(role)

    def add_roles(self, roles):
        for role in roles:
            self.add_role(role)

    def get_roles(self):
        for role in self.roles:
            yield role
