# -*- coding: utf-8 -*-
#!/usr/bin/bash
from flask import Flask
from flask_script import Manager, prompt_bool
from flask_migrate import Migrate, MigrateCommand
from flask_alchemydumps import AlchemyDumps, AlchemyDumpsCommand

from core import create_application, db

from models import *

app = create_application(__name__)

migrate = Migrate(app, db)
alchemy_dumps = AlchemyDumps(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)
manager.add_command('alchemy', AlchemyDumpsCommand)

if __name__ == '__main__':
    manager.run()
