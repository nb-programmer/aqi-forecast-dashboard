'''
General configuration options and paths
'''

import os
import pytz

BASE = os.path.dirname(__file__)

#Assume time is stored as IST
MY_TZ = pytz.timezone('Asia/Calcutta')

#Location of all models
MODEL_DIR = 'models'

#Database connection path
DATABASE = 'sqliteext:///%s' % os.path.join(MODEL_DIR, 'database.db')

MODEL_PATH = {
    #Scaler object
    "scaler": {
        "type": 'sklearn_scaler',
        "path": os.path.join(MODEL_DIR, 'AQI_SCALER.gz')
    },

    #Models
    "lstm": {
        "type": 'keras_lstm',
        "path": os.path.join(MODEL_DIR, 'AQI_LSTM_new.h5'),
        "scaler": 'scaler'
    },

    "svr": {
        "type": 'sklearn_svr',
        "path": os.path.join(MODEL_DIR, 'AQI_SVR.gz'),
        "scaler": 'scaler'
    },

    "polydeg10": {
        "type": 'sklearn_polyreg',
        "reg": {
            "path": os.path.join(MODEL_DIR, 'AQI_POLYREG_REG.gz')
        },
        "ftr": {
            "path": os.path.join(MODEL_DIR, 'AQI_POLYREG_FTR.gz')
        },
        "scaler": 'scaler'
    },

    "arima": {
        "type": 'statsmodels_arima',
        "scaler": 'scaler'
    }
}
