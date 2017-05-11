# -*- coding: utf-8 -*-
from .rbac import RBAC
from .models import RoleMixin, UserMixin

def load_user(user_id):
    from models import User
    return User.get(user_id)
