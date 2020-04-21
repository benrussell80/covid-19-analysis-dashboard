import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import scipy.stats as st
from utils import join_to_data_folder


def main():
    line_list_df = pd.read_csv(join_to_data_folder('cleaned/COVID19_line_list_data.csv'))
    datetime_columns = [
        'symptom_onset',
        'exposure_start',
        'exposure_end',
        'recovered_date',
        'death_date',
        'hospital_visit_date',
        'reporting_date'
    ]
    for col in datetime_columns:
        line_list_df[col] = pd.to_datetime(line_list_df[col], yearfirst=True)

    num_cases_that_reported_symptoms = line_list_df.symptoms[pd.notna(line_list_df.symptoms)].size

    symptom_rates = (line_list_df[[col for col in line_list_df.columns if col.startswith('experienced')]].sum() / num_cases_that_reported_symptoms).sort_values(ascending=False)
    symptom_rates = symptom_rates.rename('rate').rename_axis('symptom')

    symptom_rates.to_csv(join_to_data_folder('cleaned/symptom_rates.csv'))

    line_list_df['age_group'] = pd.cut(
        x=line_list_df.age,
        bins=[*range(0, 105, 10), 200],
        labels=[*(f'{i} - {i+9}' for i in range(0, 100, 10)), '100+'],
        include_lowest=True,
        right=False
    ).values

    age_gender_counts = line_list_df.groupby(['age_group', 'gender'])['age'].count().rename('counts')

    age_gender_proportions = (age_gender_counts / age_gender_counts.sum()).rename('proportion')

    age_gender_death_counts = line_list_df.groupby(['age_group', 'gender']).sum()['death'].fillna(0).rename('deaths')
    age_gender_death_rates = (age_gender_death_counts / age_gender_death_counts.sum()).rename('death_rate')

    line_list_analysis = pd.concat((age_gender_counts, age_gender_proportions, age_gender_death_counts, age_gender_death_rates), axis=1)

    line_list_analysis.to_csv(join_to_data_folder('cleaned/line_list_analysis.csv'))

    symptom_onset_time = (line_list_df['symptom_onset'] - line_list_df['exposure_start']).dt.days

    line_list_df['symptom_onset_delay'] = symptom_onset_time[pd.notna(symptom_onset_time)].reset_index(drop=True)

    line_list_df.to_csv(join_to_data_folder('cleaned/COVID19_line_list_data.csv'))


if __name__ == "__main__":
    main()