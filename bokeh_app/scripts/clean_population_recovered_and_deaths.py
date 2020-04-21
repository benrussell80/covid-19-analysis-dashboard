import pandas as pd
import numpy as np
import os


def main():
    HERE = os.path.dirname(__file__)
    DATA_FOLDER = os.path.join(os.path.dirname(HERE), 'data')

    # Susceptibles : population
    S_df = pd.read_csv(
        os.path.join(
            DATA_FOLDER,
            'raw', 'population_by_country.csv'
        ),
        usecols=['Country Name', 'Country Code', '2018'],
    )
    S_df.columns = ['country', 'code', 'population_2018']
    S_df.dropna(inplace=True)
    S_df.to_csv(
        os.path.join(
            DATA_FOLDER,
            'cleaned', 'populations.csv'
        ),
        index=False
    )

    # Recovered : recovered
    R_df = pd.read_csv(
        os.path.join(
            DATA_FOLDER,
            'raw', 'time_series_covid_19_recovered.csv'
        )
    )
    R_df.columns = ['region', 'country', 'latitude', 'longitude', *[date.strftime('%Y-%m-%d') for date in pd.to_datetime(R_df.columns[4:])]]
    R_df['full_name'] = R_df.apply(lambda row: ', '.join(filter(pd.notna, [row.region, row.country])), axis=1)
    china_series = R_df.loc[R_df.country=='China'].sum()
    china_series['full_name'] = 'China'
    R_df = R_df.append(china_series, ignore_index=True)
    R_df.drop(['region', 'country', 'latitude', 'longitude'], axis=1, inplace=True)
    R_df = R_df.drop('full_name', axis=1).T.rename(columns=R_df['full_name'])
    R_df.index = pd.to_datetime(R_df.index, yearfirst=True).rename('date')
    R_df.to_csv(
        os.path.join(
            DATA_FOLDER,
            'cleaned', 'time_series_covid_19_recovered.csv'
        )
    )

    # Deaths : deaths
    D_df = pd.read_csv(
        os.path.join(
            DATA_FOLDER,
            'raw', 'time_series_covid_19_deaths.csv'
        )
    )
    D_df.columns = ['region', 'country', 'latitude', 'longitude', *[date.strftime('%Y-%m-%d') for date in pd.to_datetime(D_df.columns[4:])]]
    D_df['full_name'] = D_df.apply(lambda row: ', '.join(filter(pd.notna, [row.region, row.country])), axis=1)
    china_series = D_df.loc[D_df.country=='China'].sum()
    china_series['full_name'] = 'China'
    D_df = D_df.append(china_series, ignore_index=True)
    D_df.drop(['region', 'country', 'latitude', 'longitude'], axis=1, inplace=True)
    D_df = D_df.drop('full_name', axis=1).T.rename(columns=D_df['full_name'])
    D_df.index = pd.to_datetime(D_df.index, yearfirst=True).rename('date')
    D_df.to_csv(
        os.path.join(
            DATA_FOLDER,
            'cleaned', 'time_series_covid_19_deaths.csv'
        )
    )


if __name__ == "__main__":
    main()