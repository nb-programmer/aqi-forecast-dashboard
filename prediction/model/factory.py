
import typing

from .models import *

ModelType = typing.Type[Model]

MODEL_CLASS_MAP : typing.Dict[str, ModelType] = {
    "sklearn_scaler": SKLearnScaler,
    "keras_lstm": LSTMModel,
    "sklearn_svr": SVRModel,
    "sklearn_polyreg": PolynomialModel,
    "statsmodels_arima": ARIMAModel
}

def create_model(type : str, **props):
    try:
        mdl_cls : ModelType = MODEL_CLASS_MAP[type]
    except KeyError:
        raise TypeError("Model class '%s' is not valid" % type)

    if mdl_cls is None or not issubclass(mdl_cls, Model):
        raise NotImplementedError("Model of type '%s' is not implemented yet!" % type)

    return mdl_cls(**props)
