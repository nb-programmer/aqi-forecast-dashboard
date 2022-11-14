
import os
import numpy as np
import typing

from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from statsmodels.tsa.arima.model import ARIMA

def create_dataset(dataset : np.ndarray, look_back : int):
    '''
    Sliding window generator for single feature dataset to generate differenced series
    '''
    return np.lib.stride_tricks.sliding_window_view(dataset, look_back, axis=0).reshape((-1, look_back, *dataset.shape[1:]))


class Model:
    def __init__(self, *, model = None, other_models = dict(), **kwargs):
        self._model = model
        self._other_models = other_models
        self._props = kwargs
        
    def get_scaler(self) -> typing.Union[MinMaxScaler, typing.Type[None]]:
        return self._other_models.get(self._props.get('scaler', 'scaler'))

    def preprocess_data(self, data : np.ndarray) -> np.ndarray:
        '''
        Scale data to the same amount done while training
        '''
        scaler = self.get_scaler()
        if scaler is None: return data
        return scaler._model.transform(data.reshape(-1, 1))

    def invert_preprocessed_data(self, data : np.ndarray) -> np.ndarray:
        '''
        Undo scaling done while preprocessing
        '''
        scaler = self.get_scaler()
        if scaler is None: return data
        return scaler._model.inverse_transform(data)


class SKLearnModel:
    @staticmethod
    def load(path : os.PathLike):
        from joblib import load
        return load(path)

class KerasModel:
    @staticmethod
    def load(path : os.PathLike):
        from tensorflow.keras.models import load_model
        return load_model(path)
    
class ForecastModel(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def forecast(self, pre_data : np.ndarray, num_predictions : int = 10) -> np.ndarray:
        return None
    
class SKLearnScaler(Model, SKLearnModel):
    def __init__(self, path : os.PathLike, **kwargs):
        super().__init__(model = self.load(path), **kwargs)


class LSTMModel(ForecastModel, KerasModel):
    def __init__(self, path : os.PathLike, **kwargs):
        super().__init__(model = self.load(path), **kwargs)

    def forecast(self, pre_data : np.ndarray, num_predictions : int = 10) -> np.ndarray:
        model = self._model
        
        #Get information of the model input
        _, in_pred, in_lookback = model.input_shape
        
        data = self.preprocess_data(pre_data)
        
        prediction_list = data[-in_lookback:]
        for _ in range(num_predictions):
            x = prediction_list[-in_lookback:]
            x = x.reshape((1, in_pred, in_lookback)) # It has lookback as feature columns along with layer size
            out = model.predict(x, verbose = 0)[0][0] # Our model predicts only one day at a time
            prediction_list = np.append(prediction_list, out)

        #Remove lookback inputs (keep the selected date)
        prediction_list = prediction_list[in_lookback-1:].reshape(-1, 1)
        #Undo scaling
        prediction_list = self.invert_preprocessed_data(prediction_list)
        return prediction_list
    
class PolynomialModel(ForecastModel, SKLearnModel):
    def __init__(self, reg : dict, ftr : dict, **kwargs):
        super().__init__(
            model = dict(
                reg=self.load(reg['path']),
                ftr=self.load(ftr['path'])
            ), **kwargs)

    def forecast(self, pre_data : np.ndarray, num_predictions : int = 10) -> np.ndarray:
        poly_lin_reg : LinearRegression = self._model['reg']
        poly_regs : PolynomialFeatures = self._model['ftr']
        data = self.preprocess_data(pre_data)
        
        in_lookback = 3

        prediction_list = data[-in_lookback:]
        for i in range(num_predictions):
            x = prediction_list[-in_lookback:].reshape(-1, in_lookback) # It has lookback as feature columns
            transformed_data = poly_regs.transform(x)
            out = poly_lin_reg.predict(transformed_data)[0][0]
            prediction_list = np.append(prediction_list, out) #Push back new prediction

        #Remove lookback inputs (keep the selected date)
        prediction_list = prediction_list[in_lookback-1:].reshape(-1, 1)
        
        prediction_list = self.invert_preprocessed_data(prediction_list)
        
        return prediction_list
    
class SVRModel(ForecastModel, SKLearnModel):
    def __init__(self, path : os.PathLike, **kwargs):
        super().__init__(model = self.load(path), **kwargs)

    def forecast(self, pre_data : np.ndarray, num_predictions : int = 10) -> np.ndarray:
        model : SVR = self._model
        
        data = self.preprocess_data(pre_data)
        
        in_lookback = 3

        prediction_list = data[-in_lookback:]
        for i in range(num_predictions):
            x = prediction_list[-in_lookback:].reshape(-1, in_lookback) # It has lookback as feature columns
            out = model.predict(x)[0]
            prediction_list = np.append(prediction_list, out) #Push back new prediction

        #Remove lookback inputs (keep the selected date)
        prediction_list = prediction_list[in_lookback-1:].reshape(-1, 1)
        
        prediction_list = self.invert_preprocessed_data(prediction_list)
        
        return prediction_list


class ARIMAModel(ForecastModel):
    def __init__(self, **kwargs):
        super().__init__(model = (ARIMA, dict(order=(2,0,1))), **kwargs)
        
    def forecast(self, pre_data : np.ndarray, num_predictions : int = 10) -> np.ndarray:
        data = self.preprocess_data(pre_data)
        mdl_type, mdl_opt = self._model
        model : ARIMA = mdl_type(data, **mdl_opt)
        model_fit = model.fit()
        output = model_fit.forecast(steps=num_predictions)
        prediction = self.invert_preprocessed_data(output.reshape(-1,1))
        prediction = np.insert(prediction, 0, pre_data[-1], axis=0)
        #TODO: Insert duplicate data of pre_data at index 0
        return prediction

__all__ = [
    'Model',
    'SKLearnScaler',
    'LSTMModel',
    'SVRModel',
    'PolynomialModel',
    'ARIMAModel'
]