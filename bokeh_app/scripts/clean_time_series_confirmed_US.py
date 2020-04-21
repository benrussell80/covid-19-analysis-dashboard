import pandas as pd
from utils import longitude_latitude_to_web_mercator
import os

def main():
    HERE = os.path.dirname(__file__)
    DATA_FOLDER = os.path.join(os.path.dirname(HERE), 'data')

    filename = 'time_series_covid_19_confirmed_US.csv'
    df = pd.read_csv(os.path.join(DATA_FOLDER, 'raw', filename))

    df.drop(['UID', 'iso3', 'iso2', 'code3', 'FIPS', 'Country_Region'], axis=1, inplace=True)

    df.rename(columns={'Admin2': 'county', 'Province_State': 'region', 'Lat': 'latitude', 'Long_': 'longitude', 'Combined_Key': 'full_name'}, inplace=True)

    df['web_mercator_x'], df['web_mercator_y'] = longitude_latitude_to_web_mercator(df.latitude.values, df.longitude.values)

    US_deaths_filename = 'time_series_covid_19_deaths_US.csv'
    df['population'] = pd.read_csv(os.path.join(DATA_FOLDER, 'raw', US_deaths_filename), usecols=['Population'])
    df.drop(df.loc[df.population==0].index, inplace=True)

    df.columns = [
        *df.columns[:5],
        *[date.strftime('%Y-%m-%d') for date in pd.to_datetime(df.columns[5:-3])],
        *df.columns[-3:]
    ]

    df.to_csv(os.path.join(DATA_FOLDER, 'cleaned', filename), index=False)


if __name__ == "__main__":
    main()