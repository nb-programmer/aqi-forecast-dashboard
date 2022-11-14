
import flask

from flask_restful import Api
from .forecast import Predictions, Prediction

def init_routes(app : flask.Flask):
    api = Api(app, prefix="/forecast")

    api.add_resource(Predictions, '/')
    api.add_resource(Prediction, '/<int:forecast_id>')

