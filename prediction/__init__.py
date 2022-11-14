
import logging
import logging.config

import flask
from flask_cors import CORS

from prediction.log import init_root_logger
from prediction.model import load_models
from prediction.dbaccess import init_db
from prediction.utils import format_data

import importlib

#API routes
ENABLED_APIS = ['prediction.aqi', 'prediction.forecast']

root_logger : logging.Logger = init_root_logger()

def init_app(debug : bool = False):
    root_logger.info("Debug mode is %s" % 'on' if debug else 'off')
    if debug:
        root_logger.setLevel(logging.DEBUG)

    root_logger.info("Initializing app...")

    app = flask.Flask(__name__)
    app.url_map.strict_slashes = False #CORS redirection issue fix

    root_logger.info("Initializing CORS...")
    cors = CORS(app, CORS_SEND_WILDCARD=True, expose_headers=["Content-Range"])
    
    root_logger.info("Loading database...")
    init_db(app)

    root_logger.info("Loading models...")
    load_models(app)

    if 'RESTFUL_JSON' not in app.config:
        app.config['RESTFUL_JSON'] = {}
    
    app.config['RESTFUL_JSON']['default'] = format_data

    for api_pkg in ENABLED_APIS:
        root_logger.info("Initializing routes for \"%s\"..." % api_pkg)

        #Load the "routes" module from the API sub-package
        imp_mod = '.'.join((api_pkg, 'routes'))

        try:
            api_module = importlib.import_module(imp_mod)
        except (ImportError, AttributeError):
            root_logger.exception("Unable to load API routes from module \"%s\". Make sure the module exists. Skipping." % api_module)
            continue

        #Initialize routes for this module
        api_module.init_routes(app)

    root_logger.info("Application now ready to launch")
    return app
