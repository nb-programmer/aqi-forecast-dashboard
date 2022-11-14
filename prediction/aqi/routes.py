
import flask
from flask_restful import Api

from .aqi import AQIList, AQIData

def init_routes(app : flask.Flask):
    api = Api(app, prefix="/aqi")

    api.add_resource(AQIList, '/')
    api.add_resource(AQIData, '/<string:location_name>')
    
