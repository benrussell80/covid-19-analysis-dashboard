import pandas as pd
from utils import join_to_data_folder


def main():
    world_df = pd.read_csv(join_to_data_folder('cleaned', 'time_series_covid_19_confirmed.csv'))
    US_df = pd.read_csv(join_to_data_folder('cleaned', 'time_series_covid_19_confirmed_US.csv'))

    # change to standardize -> city, county, region, country; full_name
    new_world_df = world_df.drop([
        'region', 'country', 'latitude', 'longitude', 'web_mercator_x', 'web_mercator_y'
    ], axis=1).set_index('full_name').T

    new_world_df.index = pd.to_datetime(new_world_df.index, yearfirst=True).rename('date')

    new_world_df.to_csv(join_to_data_folder('cleaned', 'country_cases_vs_time.csv'))

    new_US_df = US_df.drop([
        'latitude', 'longitude', 'county', 'region', 'web_mercator_x', 'web_mercator_y', 'population'
    ], axis=1).set_index('full_name').T

    new_US_df.index = pd.to_datetime(new_US_df.index, yearfirst=True).rename('date')

    new_US_df.to_csv(join_to_data_folder('cleaned', 'US_cases_vs_time.csv'))


if __name__ == "__main__":
    main()