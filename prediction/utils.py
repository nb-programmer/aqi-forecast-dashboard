

from datetime import datetime

from peewee import SelectQuery, Model
from playhouse.shortcuts import model_to_dict

from .config import MY_TZ
from pandas import DataFrame, DatetimeIndex, date_range

def format_data(o : object):
    '''
    JSON formatter
    '''
    if isinstance(o, datetime):
        return o.replace(tzinfo=MY_TZ).isoformat()
    elif isinstance(o, SelectQuery):
        return list(o.dicts())
    elif isinstance(o, Model):
        return model_to_dict(o)
    elif isinstance(o, DataFrame):
        return o.to_dict('records')
    return str(o)

def interpolate_date_range(df : DataFrame, drange : DatetimeIndex = None, date_col : str = None, interpolation : str = 'nearest', **interpol_args):
    if interpolation == 'none':
        return df
    if date_col is not None:
        df = df.set_index(date_col)
    if drange is None:
        drange = date_range(df.index.min(), end=df.index.max(), freq='1d')
    if 'order' not in interpol_args:
        interpol_args['order'] = 3

    return df.reindex(df.index.union(drange)).interpolate(method=interpolation, limit_direction='both', **interpol_args).clip(0, 500).reset_index(names=date_col)
    

def aqi2loc(aqi : float):
    if aqi <= 50: return 'Good'
    if aqi <= 100: return 'Moderate'
    if aqi <= 150: return 'Unhealthy for Sensitive Groups'
    if aqi <= 200: return 'Unhealthy'
    if aqi <= 300: return 'Very Unhealthy'
    return 'Hazardous'
