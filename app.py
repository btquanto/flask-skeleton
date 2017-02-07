# -*- coding: utf-8 -*-

from flask import redirect, url_for
from core import create_application

app = create_application(__name__)

# Default route
@app.route('/')
def bootstrap():
    return redirect('/home/index')

if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'])
