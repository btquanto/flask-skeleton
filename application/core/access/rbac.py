# -*- coding: utf-8 -*-

import itertools

from flask import (
    _app_ctx_stack as connection_stack,
    abort,
    request,
)

try:
    from flask_login import current_user
except ImportError:
    current_user = None

from flask_login import UserMixin as LoginUserMixin, AnonymousUserMixin

from .acl import AccessControlList
from .models import RoleMixin, UserMixin, anonymous

class _RBACState(object):
    def __init__(self, rbac, app):
        self.rbac = rbac
        self.app = app


class RBAC(object):
    def __init__(self, app=None, **kwargs):
        self.acl = AccessControlList()
        self.before_acl = {'allow': [], 'deny': []}

        self._role_model = kwargs.get('role_model', RoleMixin)
        self._user_model = kwargs.get('user_model', UserMixin)
        self._current_user_loader = kwargs.get('current_user_loader', lambda: current_user)

        self.permission_failed_hook = kwargs.get('permission_failed_hook')

        if app is not None:
            self.app = app
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app):
        app.config.setdefault('RBAC_DENY_ALL_BY_DEFAULT', False)

        self.use_white = app.config['RBAC_DENY_ALL_BY_DEFAULT']

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['rbac'] = _RBACState(self, app)

        self.acl.allow(anonymous, 'GET', app.view_functions['static'])
        app.before_first_request(self._setup_acl)

        app.before_request(self._authenticate)

    def role_model(self, cls):
        self._role_model = cls
        return cls

    def user_model(self, cls):
        self._user_model = cls
        return cls

    def current_user_loader(self, current_user_loader):
        self._current_user_loader = current_user_loader
        return current_user_loader

    def permission_failed(self, hook):
        self.permission_failed_hook = hook
        return hook

    def has_permission(self, method, endpoint, user=None):
        app = self.get_app()
        _user = user or self._current_user_loader()
        if not hasattr(_user, 'get_roles'):
            roles = [anonymous]
        else:
            roles = _user.get_roles()
        view_func = app.view_functions[endpoint]
        return self._check_permission(roles, method, view_func)

    def allow(self, roles, methods, with_children=True):
        def decorator(view_func):
            _methods = [m.upper() for m in methods]
            for r, m, v in itertools.product(roles, _methods, [view_func]):
                self.before_acl['allow'].append((r, m, v, with_children))
            return view_func
        return decorator

    def deny(self, roles, methods, with_children=False):
        def decorator(view_func):
            _methods = [m.upper() for m in methods]
            for r, m, v in itertools.product(roles, _methods, [view_func]):
                self.before_acl['deny'].append((r, m, v, with_children))
            return view_func
        return decorator

    def exempt(self, view_func):
        self.acl.exempt(view_func)
        return view_func

    def get_app(self, reference_app=None):
        if reference_app is not None:
            return reference_app
        if self.app is not None:
            return self.app
        ctx = connection_stack.top
        if ctx is not None:
            return ctx.app
        raise RuntimeError('application not registered on rbac '
                           'instance and no application bound '
                           'to current context')

    def _authenticate(self):
        app = self.get_app()
        assert app, "Please initialize your application into RBAC."
        assert self._role_model, "Please set role model before authenticate."
        assert self._user_model, "Please set user model before authenticate."
        assert self._current_user_loader, "Please set user loader before authenticate."

        current_user = self._current_user_loader()
        if current_user is not None and not isinstance(current_user, self._user_model):
            current_user = None

        endpoint = request.endpoint
        resource = app.view_functions.get(endpoint, None)

        if not resource:
            abort(404)

        method = request.method
        roles = getattr(current_user, 'get_roles', lambda: [anonymous])()
        permit = self._check_permission(roles, method, resource)

        if not permit:
            return self.permission_failed_hook()

    def _check_permission(self, roles, method, resource):
        if self.acl.is_exempt(resource):
            return True

        _roles = set()
        _methods = set(['*', method])
        _resources = set([None, resource])

        if self.use_white:
            _roles.add(anonymous)

        is_allowed = None
        _roles.update(roles)

        if not self.acl.is_set:
            self._setup_acl()

        for r, m, res in itertools.product(_roles, _methods, _resources):
            if self.acl.is_denied(r.get_name(), m, res):
                return False

            if self.acl.is_allowed(r.get_name(), m, res):
                is_allowed = True

        if self.use_white:
            permit = (is_allowed == True)
        else:
            permit = (is_allowed != False)

        return permit

    def _setup_acl(self):
        for rn, method, resource, with_children in self.before_acl['allow']:
            role = self._role_model.get_by_name(rn)
            if rn == 'anonymous':
                role = rn
            else:
                role = self._role_model.get_by_name(rn)
            self.acl.allow(role, method, resource, with_children)
        for rn, method, resource, with_children in self.before_acl['deny']:
            role = self._role_model.get_by_name(rn)
            self.acl.deny(role, method, resource, with_children)
        self.acl.is_set = True
