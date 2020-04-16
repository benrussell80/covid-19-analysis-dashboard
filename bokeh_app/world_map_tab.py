import datetime

from bokeh.models import (Button, ColorBar, DataTable, DateSlider, Panel,
                          TableColumn, LogTicker)
from bokeh.palettes import Spectral6
from bokeh.plotting import figure
from bokeh.tile_providers import CARTODBPOSITRON, get_provider
from bokeh.transform import log_cmap
from bokeh.layouts import column, row

from utils import START_DATE, scale

from sources import get_time_series_confirmed_data


def create_world_map_tab():
    "Factory for creating first tab of app."

    ## Data Sources
    source_df, source_CDS = get_time_series_confirmed_data()

    ## Map
    color_mapper = log_cmap(field_name='number', palette=Spectral6, low=1, high=1e6)

    TOOLTIPS = [
        ('Region', '@full_name'),
        ('Num. Cases', '@number{0,0}')
    ]

    map_figure = figure(
        title='Confirmed COVID-19 Cases by Region',
        tooltips=TOOLTIPS,
        x_range=(-16697923.62, 18924313),
        y_range=(-8399737.89, 8399737.89),
        x_axis_type='mercator',
        y_axis_type='mercator',
        active_scroll='wheel_zoom'
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
            source_CDS.data['number'] = source_df[date_string]
            source_CDS.data['sizes'] = source_df[date_string].apply(scale)
        except KeyError:
            pass

    slider = DateSlider(title='Date', start=START_DATE, end=datetime.date.today(), step=1, value=START_DATE)
    slider.on_change('value', slider_callback)

    ## Data Table
    columns = [
        TableColumn(field='full_name', title='Region'),
        TableColumn(field='number', title='Cases')
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
        column([data_table, cancel_selection_button]),
    ])

    return Panel(child=child, title='World Map')
