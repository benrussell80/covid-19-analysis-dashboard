import datetime
from functools import partial

import numpy as np
import pandas as pd
from bokeh.layouts import column, row
from bokeh.models import (ColumnDataSource, HoverTool, Legend, LegendItem,
                          MultiSelect, Panel, CheckboxGroup, LogScale, LinearScale)
from bokeh.palettes import magma, viridis, gray, Viridis256
from bokeh.plotting import figure

from sources import get_time_series_confirmed_data, get_country_cases_vs_time


def create_world_cases_time_series_tab():
    ## Data Sources
    source_df, source_CDS = get_country_cases_vs_time()
    
    ## Line Plots
    line_figure = figure(
        x_axis_type='datetime',
        y_axis_type='log',
        title='World Confirmed Cases by Region',
        x_axis_label='Date',
        y_axis_label='Number of Confirmed Cases (Logarithmic Scale)',
        active_scroll='wheel_zoom'
    )

    starting_regions = [
        'China',
        'US',
        'Italy'
    ]
    excluded_columns_set = {'index', 'date'}

    doubling_lines_props = {
        'alpha': 0.6,
        'muted_alpha': 0.2,
        'line_width': 3,
        'source': source_CDS,
        'x': 'date',
        'visible': True
    }

    for number, text, color in zip([4, 7, 14], ['four', 'seven', 'fourteen'], gray(6)[2:5]):
        column_name = f'{text}_day_doubling'
        excluded_columns_set.add(column_name)
        source_CDS.data[column_name] = 2 ** (np.arange(len(source_CDS.data['index'])) / number)
        line_figure.line(
            y=column_name,
            legend_label=f'{number}-day Doubling Time',
            line_color=color,
            name=column_name,
            **doubling_lines_props
        )

    line_params = {
        'x': 'date',
        'source': source_CDS,
        'line_width': 4,
        'alpha': 0.6
    }

    lines = {
        key: line_figure.line(
            y=key,
            name=key,
            line_color=color,
            **line_params
        )
        for key, color in zip(starting_regions, viridis(len(starting_regions)))
    }

    line_figure.legend.location = 'top_left'
    line_figure.legend.click_policy = 'hide'

    hover_tool = HoverTool(
        tooltips=[
            ('Date', '@date{%F}'),
            ('Region', '$name'),
            ('Number of Cases', '@$name{0,0}')
        ],
        formatters={
            '@date': 'datetime',
        },
        renderers=[
            *line_figure.renderers
        ],
        # mode='vline'
    )

    line_figure.add_tools(hover_tool)

    ## Region Selector
    labels = [
        key
        for key in source_CDS.data.keys()
        if key not in excluded_columns_set
    ]

    def region_select_callback(attr, old, new):
        new_lines = set(new) - set(old)
        old_lines = set(old) - set(new)

        for key in old_lines:
            lines[key].visible = False

        for key in new_lines:
            if key in lines.keys():
                lines[key].visible = True
            else:
                lines[key] = line_figure.line(
                    y=key,
                    name=key,
                    line_color=np.random.choice(Viridis256),
                    **line_params
                )
                hover_tool.renderers = [*hover_tool.renderers, lines[key]]

    region_select = MultiSelect(
        title='Select Regions to Show',
        value=starting_regions,
        options=labels,
        sizing_mode='stretch_height'
    )
    region_select.on_change('value', region_select_callback)

    ## Create Layout
    child = row([
        column([line_figure]),
        column([region_select]),
    ])

    return Panel(child=child, title='World Cases Time Series')
