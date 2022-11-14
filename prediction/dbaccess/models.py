
from peewee import *
from playhouse.sqlite_ext import JSONField

from . import db
from ..utils import format_data

from datetime import datetime
from json import dumps, loads

def custom_dumps(o : object):
    return dumps(o, default=format_data)

class AQI(db.Model):
    class Meta:
        table_name = 'pcb_dataset'

    id = AutoField()
    sampling_ts = DateTimeField(null=True)
    location_name = CharField()
    metric_aqi = FloatField(null=True)
    metric_so2 = FloatField(null=True)
    metric_no2 = FloatField(null=True)
    metric_pm10 = FloatField(null=True)
    metric_pm2_5 = FloatField(null=True)

class Forecast(db.Model):
    id = AutoField()
    method = CharField()
    create_ts = DateTimeField(default=datetime.now)
    forecast_start = DateTimeField(null=True)
    interpolation = CharField()
    data_original = JSONField(json_dumps=custom_dumps)
    data_used = JSONField(json_dumps=custom_dumps)
    data_forecast = JSONField(json_dumps=custom_dumps)
    forecast_meta = JSONField(json_dumps=custom_dumps)
