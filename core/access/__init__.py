# -*- coding: utf-8 -*-
from flask import g, current_app
from .rbac import RBAC
from .models import RoleMixin, UserMixin

def load_user(user_id):
    from models import User
    return User.get(user_id)

def get_current_user():
    try:
        return g.current_user
    except:
        return None
