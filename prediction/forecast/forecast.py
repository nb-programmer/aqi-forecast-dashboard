
from flask_restful import Resource
from flask import request, abort

import logging

from peewee import SelectQuery

import numpy as np
import pandas as pd

from ..dbaccess.models import Forecast, AQI
from ..dbaccess.utils import paginate, sortable

from ..model import perform_forecast_steps_auto
from ..utils import interpolate_date_range, aqi2loc

LOG = logging.getLogger(__name__)

def get_sample_data(location_name : str, forecast_date : pd.Timestamp, in_future : bool = False, num_points : int = 10) -> SelectQuery:
    if in_future:
        return AQI.select(
            AQI.sampling_ts,
            AQI.metric_aqi
        ).where(
            (AQI.location_name == location_name) & (AQI.sampling_ts >= forecast_date.to_pydatetime())
        ).order_by(
            AQI.sampling_ts.asc()
        ).limit(num_points)
    else:
        return AQI.select(
            AQI.sampling_ts,
            AQI.metric_aqi
        ).where(
            (AQI.location_name == location_name) & (AQI.sampling_ts <= forecast_date.to_pydatetime())
        ).order_by(
            #To get latest data
            AQI.sampling_ts.desc()
        ).limit(num_points) # The lookback value of most models
    
class Predictions(Resource):
    @paginate
    @sortable
    def get(self):
        return Forecast.select(
            Forecast.id,
            Forecast.method,
            Forecast.forecast_start,
            Forecast.data_forecast.length().alias("days"),
            Forecast.forecast_meta['avg'].alias('avg'),
            Forecast.forecast_meta['LOC'].alias('LOC'),
            Forecast.forecast_meta['ds'].alias('ds')
        )
    
    def post(self):
        model = request.json.get("method", "lstm") #Model to use
        num_days = request.json.get("days", 10) #Days to forecast
        aqi_interpolation = request.json.get("interpolation", 'nearest') #Interpolation of in-between points
        loc = request.json.get("dataset") #Which dataset (city) to use
        forecast_start = request.json.get("forecast_at") #Starting date to look back for data points

        if loc is None:
            abort("'dataset' is not specified")
        
        forecast_start = pd.to_datetime(forecast_start, yearfirst=True)

        LOG.info("Generating prediction of %d days using %s" % (num_days, model))

        #Original data points
        data_points = pd.DataFrame(get_sample_data(loc, forecast_start).dicts()).sort_values(by=['sampling_ts'])
        
        #We are predicting from the next day of last date in data
        start_date = data_points.sampling_ts.max()# + pd.Timedelta('1d')

        data_daily_range = pd.date_range(data_points.sampling_ts.min(), end=data_points.sampling_ts.max(), freq='1d')

        #Interpolate missing points, if any
        data_points_interpol = interpolate_date_range(data_points, data_daily_range, 'sampling_ts', interpolation=aqi_interpolation, order=3)

        #Only AQI values
        input_sequence = data_points_interpol.metric_aqi.values
        
        #Perform the prediction on given data
        forecasted_aqi = perform_forecast_steps_auto(
            model=model,
            data=input_sequence,
            num_predictions=num_days
        )

        if forecasted_aqi is None or not isinstance(forecasted_aqi, np.ndarray):
            #Failed to create, do not proceed
            return None, 500

        #Convert to list of dict
        forecasted_scatter = list(
            map(
                lambda x: dict(sampling_ts=x[0], metric_aqi=x[1]),
                zip(pd.date_range(start=start_date, periods=num_days, freq='1d'), forecasted_aqi.flatten())
            )
        )

        avg_aqi = np.average(forecasted_aqi)

        forecast_metadata = {
            'avg': avg_aqi,
            'ds': loc,
            'LOC': aqi2loc(avg_aqi)
        }
        
        return Forecast.create(
            method=model,
            forecast_start=start_date.to_pydatetime(),
            interpolation=aqi_interpolation,
            data_original=data_points,
            data_used=data_points_interpol,
            data_forecast=forecasted_scatter,
            forecast_meta=forecast_metadata
        )

    
class Prediction(Resource):
    def get(self, forecast_id : int):
        return Forecast.get(Forecast.id == forecast_id)

    def delete(self, forecast_id : int):
        return Forecast.get(Forecast.id == forecast_id).delete_instance()

class PredictionCompare(Resource):
    def get(self, forecast_id : int):
        fc : Forecast = Forecast.select(Forecast.forecast_meta, Forecast.forecast_start).where(Forecast.id == forecast_id).get()
        metadata : dict = fc.forecast_meta
        ds_loc : str = metadata['ds']
        fc_start = fc.forecast_start

        return {
            'id': forecast_id,
            'data': get_sample_data(ds_loc, pd.to_datetime(fc_start), True)
        }
