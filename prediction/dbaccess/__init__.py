from playhouse.flask_utils import FlaskDB

from prediction.config import DATABASE

import flask

db = FlaskDB(database=DATABASE)

def init_db(app : flask.Flask):
    db.init_app(app)
