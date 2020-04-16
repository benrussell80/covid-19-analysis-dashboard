# analysis (e.g. doubling times, forecasting, most at risk groups)
from functools import partial

import numpy as np
import pandas as pd
import scipy.stats as st
from bokeh.colors import RGB
from bokeh.layouts import column, row
from bokeh.models import (Band, Button, ColumnDataSource, DataTable, HoverTool,
                          NumberFormatter,
                          Legend, LegendItem, Line, MultiSelect, Panel,
                          TableColumn, Tabs)
from bokeh.palettes import Viridis256, viridis
from bokeh.plotting import figure

from sources import (get_countries_logistic_fitting_params,
                     get_country_cases_vs_time, get_line_list_analysis,
                     get_symptom_rates, get_US_cases_vs_time,
                     get_US_logistic_fitting_params)
from utils import START_DATE, START_DATE_STRING, hex_string_to_rgb


def create_logistic_growth_subtab(params_getter, time_series_getter, starting_regions, tab_title):
    # Data Sources
    params_df, params_CDS = params_getter()
    time_series_df, time_series_CDS = time_series_getter()

    dates = np.arange(START_DATE_STRING, '2020-07-01', dtype='datetime64[D]')

    bands_CDS = ColumnDataSource({
        'date': dates
    })
    
    lines_CDS = ColumnDataSource({
        'date': dates
    })

    # Set up Figure
    plot = figure(
        x_axis_type='datetime',
        x_axis_label='Date',
        y_axis_label='Number of Cases',
        title='Logistic Growth Modeling',
        active_scroll='wheel_zoom'
    )
    plot.yaxis.formatter.use_scientific = False

    lines = {}  # region, line pairs housing which have been drawn already
    bands = {}  # region, band pairs housing which have been drawn already

    def logistic_function(x, L, x0, k):
        return L / (1 + np.exp(-k*(x-x0)))

    def z_star(conf_level):
        return st.norm.ppf(1 - (1 - conf_level) / 2)

    def get_offset_from_start_date(region):
        subdf = time_series_df[region]
        nonzero_subdf = subdf[subdf>0]

        offset = (nonzero_subdf.index[0] - pd.to_datetime(START_DATE)).days

        return offset

    def draw_prediction_line(region, **kwargs):
        plot_params = {
            'line_width': 4,
            'line_alpha': 0.4,
            'line_dash': 'dashed'
        }

        plot_params.update(kwargs)

        L, x0, k, L_std, x0_std, k_std = params_CDS.data[region]
        xs = np.arange(lines_CDS.data['date'].size)
        offset = get_offset_from_start_date(region)
        line = logistic_function(xs, L, x0 + offset, k)
        lines_CDS.data[region] = line
        lines[f'{region}_prediction'] = plot.line(
            x='date', y=region, source=lines_CDS,
            name=region,
            **plot_params
        )

    def draw_prediction_band(region, conf_level, **kwargs):
        plot_params = {
            'line_alpha': 0,
            'fill_alpha': 0.4
        }

        plot_params.update(kwargs)

        L, x0, k, L_std, x0_std, k_std = params_CDS.data[region]
        xs = np.arange(lines_CDS.data['date'].size)
        offset = get_offset_from_start_date(region)
        bands_CDS.data[f'{region}_lower'], bands_CDS.data[f'{region}_upper'] = (
            logistic_function(xs, L - L_std * z_star(conf_level), x0 + offset, k), 
            logistic_function(xs, L + L_std * z_star(conf_level), x0 + offset, k)
        )

        bands[region] = Band(
            base='date', lower=f'{region}_lower', upper=f'{region}_upper',
            source=bands_CDS, level='underlay', **plot_params
        )
        plot.add_layout(bands[region])

    def draw_data_line(region, **kwargs):
        plot_params = {
            'line_width': 4,
        }

        plot_params.update(kwargs)

        lines[region] = plot.line(
            x='date', y=region, source=time_series_CDS,
            name=region,
            **plot_params
        )

    confidence_level = 0.95

    for region, color in zip(starting_regions, viridis(len(starting_regions))):
        color = RGB(*hex_string_to_rgb(color))
        darkened_color = color.darken(.15)
        lightened_color = color.lighten(.15)
    
        # draw prediction band
        draw_prediction_band(region, confidence_level, fill_color=color)
    
        # draw prediction line
        draw_prediction_line(region, line_color=darkened_color)
        
        # draw data line
        draw_data_line(region, line_color=color)

    # Hover Tool
    hover_tool = HoverTool(
        tooltips=[
            ('Date', '@date{%F}'),
            ('Region', '$name'),
            ('Num. Cases', '@$name{0,0}')
        ],
        formatters={
            '@date': 'datetime',
        }
    )
    plot.add_tools(hover_tool)
    hover_tool.renderers = list(lines.values())

    # Legend
    prediction_line_glyph = plot.line(line_color='black', line_dash='dashed', name='prediction_line_glyph', line_width=4)
    prediction_line_glyph.visible = False
    data_line_glyph = plot.line(line_color='black', name='data_line_glyph', line_width=4)
    data_line_glyph.visible = False
    confidence_interval_glyph = plot.patch(
        [0, 0, 1, 1],
        [0, 1, 1, 0],
        name='confidence_interval_glyph',
        line_color='black', line_width=1, 
        fill_alpha=0.3, fill_color='black',
    )
    confidence_interval_glyph.visible = False

    legend = Legend(items=[
        LegendItem(label="Data", renderers=[plot.select_one({'name': 'data_line_glyph'})]),
        LegendItem(label="Prediction", renderers=[plot.select_one({'name': 'prediction_line_glyph'})]),
        LegendItem(label="95% Confidence Interval", renderers=[plot.select_one({'name': 'confidence_interval_glyph'})])
    ], location='top_left')
    plot.add_layout(legend)

    ## Prevent legend glyphs from affecting plotting ranges
    def fit_to_visible_lines():
        plot.x_range.renderers = list(filter(lambda line: line.visible, lines.values()))
        plot.y_range.renderers = list(filter(lambda line: line.visible, lines.values()))

    # Region Selector
    excluded_columns_set = {'index', 'parameters'}

    labels = [
        key
        for key in params_CDS.data.keys()
        if key not in excluded_columns_set
    ]

    def region_select_callback(attr, old, new):
        new_lines = set(new) - set(old)
        old_lines = set(old) - set(new)

        for key in old_lines:
            lines[key].visible = False
            lines[f'{key}_prediction'].visible = False
            bands[key].visible = False

        for key in new_lines:
            if key in lines.keys():
                lines[key].visible = True
                lines[f'{key}_prediction'].visible = True
                bands[key].visible = True
            else:
                color = RGB(
                    *hex_string_to_rgb(
                        np.random.choice(
                            Viridis256
                        )
                    )
                )
                darkened_color = color.darken(.15)
                lightened_color = color.lighten(.15)

                draw_prediction_line(key, line_color=darkened_color)
                draw_prediction_band(key, conf_level=confidence_level, fill_color=lightened_color)
                draw_data_line(key, line_color=color)

                hover_tool.renderers = [
                    *hover_tool.renderers,
                    lines[key],
                    lines[f'{key}_prediction']
                ]

    region_select = MultiSelect(
        title='Select Regions to Show',
        value=starting_regions,
        options=labels,
        sizing_mode='stretch_height'
    )
    region_select.on_change('value', region_select_callback)

    # Final Setup
    fit_to_visible_lines()

    child = row(
        column([plot]),
        column([region_select])
    )

    return Panel(child=child, title=tab_title)


def create_symptom_stats_subtab():
    source_df, source_CDS = get_symptom_rates()
    source_CDS.data['cleaned_symptom'] = [
        symptom[12:].replace('_', ' ').title()
        for symptom in source_CDS.data['symptom']
    ]

    columns = [
        TableColumn(field='cleaned_symptom', title='Symptom'),
        TableColumn(field='rate', title='Fraction of Cases', formatter=NumberFormatter(format='0.00%')),
    ]
    data_table = DataTable(columns=columns, source=source_CDS, sizing_mode='stretch_height')

    child = row(
        column([data_table])
    )
    return Panel(child=child, title='Symptoms Experienced')


def create_age_gender_stats_subtab():
    source_df, source_CDS = get_line_list_analysis()

    columns = [
        TableColumn(field='age_group', title='Age Group'),
        TableColumn(field='gender', title='Gender'),
        TableColumn(field='proportion', title='Fraction of Cases', formatter=NumberFormatter(format='0.00%')),
        TableColumn(field='death_rate', title='Death Rate', formatter=NumberFormatter(format='0.00%'))
    ]

    data_table = DataTable(columns=columns, source=source_CDS, sizing_mode='stretch_height')

    child = row(
        column([data_table])
    )

    return Panel(child=child, title='Infection Statistics by Age & Gender')


create_world_logistic_growth_tab = partial(
    create_logistic_growth_subtab,
    get_countries_logistic_fitting_params,
    get_country_cases_vs_time,
    ['US', 'Italy', 'China'],
    'World Logistic Growth Fitting'
)

create_us_logistic_growth_tab = partial(
    create_logistic_growth_subtab,
    get_US_logistic_fitting_params,
    get_US_cases_vs_time,
    [
        'New York City, New York, US',
        'Westchester, New York, US',
        'Los Angeles, California, US',
        'Cook, Illinois, US',
        'King, Washington, US',
        'Clark, Nevada, US',
    ],
    'US Logistic Growth Fitting'
)

def create_analysis_tab():
    child = Tabs(tabs=[
        create_world_logistic_growth_tab(),
        create_us_logistic_growth_tab(),
        create_symptom_stats_subtab(),
        create_age_gender_stats_subtab(),
    ])

    return Panel(child=child, title='Analysis')
