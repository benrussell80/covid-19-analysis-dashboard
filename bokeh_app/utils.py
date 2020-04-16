import datetime
import math
import os
from functools import partial


def scale(value, min_size=4, log_base=math.e):
    try:
        return math.log(value, log_base) + min_size
    except ValueError:
        return 0


START_DATE = datetime.date(2020, 1, 22)
START_DATE_STRING = START_DATE.strftime('%Y-%m-%d')

DATA_FOLDER = os.path.join(
    os.path.dirname(__file__),
    'data'
)

join_to_data_folder = partial(os.path.join, DATA_FOLDER)


def hex_string_to_rgb(hex_string: str):
    "Converts a hex string formatted as '#XXXXXX' to RGB as (r, g, b)."
    color = int(hex_string[1:], 16)
    r, g, b = color.to_bytes(3, 'big')
    return r, g, b