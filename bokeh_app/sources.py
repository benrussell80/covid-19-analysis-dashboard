from functools import partial, wraps

import pandas as pd
from bokeh.models import ColumnDataSource

from utils import START_DATE, START_DATE_STRING, join_to_data_folder, scale


def get_df_and_CDS(filename):
    "Base factory for fetching pandas DataFrame and bokeh ColumnDataSource from a file."
    file = join_to_data_folder('cleaned', filename)
    df = pd.read_csv(file)
    CDS = ColumnDataSource(df)

    return df, CDS


def include_number_and_sizes(func):
    "Add number and sizes columns to ColumnDataSource that help with plotting data for a particular date."
    @wraps(func)
    def wrapper(*args, **kwargs):
        df, CDS = func(*args, **kwargs)
        CDS.data['number'] = df[START_DATE_STRING]
        CDS.data['sizes'] = df[START_DATE_STRING].apply(scale)
        return df, CDS
    return wrapper


def convert_date_column(func):
    "Converts date column of CDS to datetime."
    @wraps(func)
    def wrapper(*args, **kwargs):
        df, CDS = func(*args, **kwargs)
        df.set_index('date', inplace=True)
        df.index = pd.to_datetime(df.index, yearfirst=True)
        CDS.data['date'] = pd.to_datetime(CDS.data['date'], yearfirst=True)
        return df, CDS
    return wrapper


get_line_list_data = partial(get_df_and_CDS, 'COVID19_line_list_data.csv')

get_country_cases_vs_time = convert_date_column(partial(get_df_and_CDS, 'country_cases_vs_time.csv'))

get_US_cases_vs_time = convert_date_column(partial(get_df_and_CDS, 'US_cases_vs_time.csv'))

get_time_series_confirmed_US_data = include_number_and_sizes(partial(get_df_and_CDS, 'time_series_covid_19_confirmed_US.csv'))

get_time_series_confirmed_data = include_number_and_sizes(partial(get_df_and_CDS, 'time_series_covid_19_confirmed.csv'))

get_countries_logistic_fitting_params = partial(get_df_and_CDS, 'countries_logistic_fitting_params.csv')

get_US_logistic_fitting_params = partial(get_df_and_CDS, 'US_logistic_fitting_params.csv')

get_symptom_rates = partial(get_df_and_CDS, 'symptom_rates.csv')

get_line_list_analysis = partial(get_df_and_CDS, 'line_list_analysis.csv')