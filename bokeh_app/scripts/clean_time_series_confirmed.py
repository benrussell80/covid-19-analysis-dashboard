import pandas as pd
from utils import longitude_latitude_to_web_mercator
import os
import numpy as np

def main():
    HERE = os.path.dirname(__file__)
    DATA_FOLDER = os.path.join(os.path.dirname(HERE), 'data')

    filename = 'time_series_covid_19_confirmed.csv'
    df = pd.read_csv(os.path.join(DATA_FOLDER, 'raw', filename))

    df.head()

    df.columns = [
        'region',
        'country',
        'latitude',
        'longitude',
        *[
            date.strftime('%Y-%m-%d')
            for date in pd.to_datetime(df.columns[4:])
        ]
    ]

    def join_region_country(row):
        return ', '.join(filter(pd.notna, [row.region, row.country]))

    df['full_name'] = df[['region', 'country']].apply(join_region_country, axis=1)

    df['web_mercator_x'], df['web_mercator_y'] = longitude_latitude_to_web_mercator(
        df['latitude'].values, df['longitude'].values
    )

    china_df = df.loc[df.country=='China']
    china_long_lat = china_df[['latitude', 'longitude']].mean()
    china_web_mercators = longitude_latitude_to_web_mercator(
        china_long_lat['latitude'], china_long_lat['longitude']
    )
    china_totals = china_df.drop([
        'region', 'country', 'latitude', 'longitude', 'web_mercator_x', 'web_mercator_y', 'full_name'
    ], axis=1).sum().T

    china_totals['web_mercator_x'], china_totals['web_mercator_y'] = china_web_mercators
    china_totals['latitude'], china_totals['longitude'] = china_long_lat['latitude'], china_long_lat['longitude']
    china_totals['full_name'], china_totals['region'], china_totals['country'] = ('China', np.nan, 'China')

    df = df.append(china_totals, ignore_index=True)

    df.to_csv(os.path.join(DATA_FOLDER, 'cleaned', filename), index=False)


if __name__ == "__main__":
    main()