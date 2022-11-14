
from typing import Callable, Any
from peewee import SelectQuery, SQL

from flask import request
from flask_restful.utils import unpack
import json

def paginate(func : Callable[[Any], SelectQuery]):
    def _wraps(*args, **kwargs):
        item_range = request.args.get('range', default=(0, 9), type=json.loads)
        row_start = item_range[0]
        row_count = item_range[1] - item_range[0] + 1
        q, code, headers = unpack(func(*args, **kwargs))
        headers.update({"Content-Range": "items %d-%d/%d" % (row_start+1,min(len(q), row_start+row_count),len(q))})
        return q.offset(row_start).limit(row_count), code, headers
    return _wraps

def sortable(func : Callable[[Any], SelectQuery]):
    def _wraps(*args, **kwargs):
        sort_column, sort_criteria = request.args.get('sort', default=('id', 'asc'), type=json.loads)
        q, code, headers = unpack(func(*args, **kwargs))
        order_query = SQL(sort_column)
        if sort_criteria.lower() == 'asc':
            order_query = order_query.asc()
        elif sort_criteria.lower() == 'desc':
            order_query = order_query.desc()
        return q.order_by(order_query), code, headers
    return _wraps