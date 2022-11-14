
import flask
import numpy as np
import logging

from .factory import create_model
from prediction.config import MODEL_PATH

MODELS_TO_LOAD = MODEL_PATH.keys()

LOG = logging.getLogger(__name__)

def load_models(app : flask.Flask):
    all_models = dict()
    app.config['model'] = all_models

    for mdl in MODELS_TO_LOAD:
        LOG.info("Loading model \"%s\"..." % mdl)
        try:
            all_models[mdl] = create_model(other_models=all_models, **MODEL_PATH[mdl])
        except:
            LOG.exception("Failed to load model \"%s\", skipping. Reason:" % mdl)


def perform_forecast_steps_auto(model : str, data : np.ndarray, num_predictions : int = 10) -> np.ndarray:
    '''
    Helper to call correct forecast function
    '''
    return flask.current_app.config['model'][model].forecast(data, num_predictions)
