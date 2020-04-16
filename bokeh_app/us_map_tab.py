import datetime

from bokeh.layouts import column, row
from bokeh.models import (Button, ColorBar, DataTable, DateSlider, Panel,
                          TableColumn, LogTicker)
from bokeh.palettes import Spectral6
from bokeh.plotting import figure
from bokeh.tile_providers import CARTODBPOSITRON, get_provider
from bokeh.transform import log_cmap

from sources import get_time_series_confirmed_US_data
from utils import START_DATE, START_DATE_STRING, scale


def create_us_map_tab():
    "Factory for creating second tab of app: US Only Data"

    ## Data Sources
    source_df_confirmed, source_CDS = get_time_series_confirmed_US_data()
    source_CDS.data['number_per_capita'] = source_df_confirmed[START_DATE_STRING] / source_df_confirmed['population']

    ## Map
    color_mapper = log_cmap(field_name='number', palette=Spectral6, low=1, high=1e6)

    TOOLTIPS = [
        ('County/Region', '@county'),
        ('State/Province', '@region'),
        ('Population', '@population'),
        ('Cases', '@number'),
        ('Cases Per Capita', '@number_per_capita')
    ]

    map_figure = figure(
        title='Confirmed COVID-19 Cases in the United States',
        tooltips=TOOLTIPS,
        x_range=(-18367715, -6901808.43),
        y_range=(0, 13377019.78),
        x_axis_type='mercator',
        y_axis_type='mercator',
        active_scroll='wheel_zoom',
    )

    tile_provider = get_provider(CARTODBPOSITRON)
    map_figure.add_tile(tile_provider)
    map_figure.circle(
        x='web_mercator_x',
        y='web_mercator_y',
        source=source_CDS,
        size='sizes',
        color=color_mapper
    )

    ## Colorbar
    color_bar = ColorBar(title='Num. Cases', title_standoff=20, color_mapper=color_mapper['transform'], label_standoff=20, width=8, location=(0, 0), ticker=LogTicker())
    color_bar.formatter.use_scientific = False
    map_figure.add_layout(color_bar, 'right')

    ## Slider
    def slider_callback(attr, old, new):
        delta = datetime.timedelta(milliseconds=new)
        date = datetime.date(1970, 1, 1) + delta
        date_string = date.strftime('%Y-%m-%d')

        try:
            source_CDS.data['number'] = source_df_confirmed[date_string]
            source_CDS.data['sizes'] = source_df_confirmed[date_string].apply(scale)
            source_CDS.data['number_per_capita'] = source_df_confirmed[date_string] / source_df_confirmed['population']
        except KeyError:
            pass

    slider = DateSlider(title='Date', start=START_DATE, end=datetime.date.today(), step=1, value=START_DATE)
    slider.on_change('value', slider_callback)

    ## Data Table
    columns = [
        TableColumn(field='county', title='County/Region'),
        TableColumn(field='region', title='State/Province'),
        TableColumn(field='population', title='Population'),
        TableColumn(field='number', title='Cases'),
        TableColumn(field='number_per_capita', title='Cases Per Capita'),
    ]

    data_table = DataTable(
        source=source_CDS,
        columns=columns,
    )

    ## Cancel Selection Button
    def cancel_selection_callback():
        source_CDS.selected.indices = []

    cancel_selection_button = Button(label='Clear Selection', button_type='warning')
    cancel_selection_button.on_click(cancel_selection_callback)

    child = row([
        column([slider, map_figure]),
        column([data_table, cancel_selection_button])
    ])

    return Panel(child=child, title='United States Map')
