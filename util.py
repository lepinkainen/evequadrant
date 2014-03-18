# utils
from datetime import datetime
from dateutil.relativedelta import *

def to_roman(n):
    return ['I', 'II', 'III', 'IV', 'V'][n - 1]

def timestamp_to_string(timestamp, now = None):
    if not now:
        now = datetime.now()
    td = relativedelta(datetime.fromtimestamp(timestamp), now)
    return "%dd %dh %dm" % (td.days, td.hours, td.minutes)

