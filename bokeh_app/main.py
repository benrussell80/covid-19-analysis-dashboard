import datetime

from bokeh.models import Tabs
from bokeh.plotting import curdoc

from world_map_tab import create_world_map_tab
# from us_map_tab import create_us_map_tab
from world_cases_time_series_tab import create_world_cases_time_series_tab
from us_cases_time_series_tab import create_us_cases_time_series_tab
from case_details_tab import create_case_details_tab
from analysis_tab import create_analysis_tab

tabs = Tabs(
    tabs=[
        create_world_map_tab(),
        # create_us_map_tab(),
        create_world_cases_time_series_tab(),
        create_us_cases_time_series_tab(),
        create_case_details_tab(),
        create_analysis_tab()
    ],
    tabs_location='above'
)

curdoc().add_root(tabs)
curdoc().title = "COVID-19 Data"
