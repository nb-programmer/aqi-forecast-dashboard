
from flask import abort, request

from flask_restful import Resource

from ..dbaccess.models import AQI
from ..dbaccess.utils import paginate, sortable
from ..utils import interpolate_date_range

from peewee import SelectQuery, fn
import pandas as pd

class AQIList(Resource):
    '''
    List of locations
    '''
    @paginate
    @sortable
    def get(self):
        return AQI.select(
            AQI.location_name.alias('id'),
            AQI.location_name.alias('name'),
            fn.min(AQI.sampling_ts).alias('from_date'),
            fn.max(AQI.sampling_ts).alias('to_date'),
            fn.avg(AQI.metric_aqi).alias('average_aqi')
        ).group_by(AQI.location_name)

class AQIData(Resource):
    def get(self, location_name : str):
        ipol : str = request.args.get('i', 'none')

        q : SelectQuery = AQI.select(
            AQI.id,
            AQI.sampling_ts,
            AQI.metric_aqi
        ).where(
            AQI.location_name == location_name
        ).order_by(AQI.sampling_ts.asc())

        df : pd.DataFrame = pd.DataFrame(q.dicts())

        df = interpolate_date_range(df, date_col='sampling_ts', interpolation=ipol, order=2)
        
        return {
            "id": location_name,
            "data": df
        }

    def delete(self, location_name : str):
        abort(403)