# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, current_app as app, jsonify, request
from jinja2 import TemplateNotFound

node = Blueprint("home", __name__, template_folder="templates")

@node.route("/index")
def index():
    return "Hello World!!!"

@node.route('/login', methods=['GET', 'POST'])
def login():
    return "Login"
