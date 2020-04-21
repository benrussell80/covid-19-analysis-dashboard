import pandas as pd
import numpy as np
import os
from scipy.optimize import curve_fit
from utils import join_to_data_folder


def main():
    country_cases_df = pd.read_csv(join_to_data_folder('cleaned', 'country_cases_vs_time.csv'))
    country_cases_df.set_index('date', inplace=True)
    country_cases_df.index = pd.to_datetime(country_cases_df.index, yearfirst=True)

    def logistic_function(x, L, x0, k):
        return L / (1 + np.exp(-k * (x - x0)))

    def get_fit_params(column):
        new_column = column[column>0]
        
        nans = np.empty(6)
        nans[:] = np.nan
        
        if new_column.size < 30:
            return nans
        
        bounds = (
            (0, -365, 0),
            (1e7, 365, 3)
        )
        
        try:
            popt, pcov = curve_fit(logistic_function, np.arange(new_column.size), new_column.values, bounds=bounds)
        except RuntimeError:
            return nans
        else:
            stds = np.sqrt(np.diag(pcov))
            return [*popt, *stds]

    fitted_logistic_parameters = country_cases_df.apply(get_fit_params).apply(pd.Series).T

    fitted_logistic_parameters.index = ['L', 'x0', 'k', 'L_std', 'x0_std', 'k_std']
    fitted_logistic_parameters.index.rename('parameters', inplace=True)

    fitted_logistic_parameters = fitted_logistic_parameters.replace(np.inf, np.nan).dropna(axis=1)

    # drop cols where L_std > L
    cols_to_drop = []
    for col in fitted_logistic_parameters.columns:
        if fitted_logistic_parameters.loc['L_std', col] > fitted_logistic_parameters.loc['L', col]:
            cols_to_drop.append(col)

    fitted_logistic_parameters.drop(cols_to_drop, axis=1, inplace=True)

    fitted_logistic_parameters.to_csv(join_to_data_folder('cleaned', 'countries_logistic_fitting_params.csv'))


if __name__ == "__main__":
    main()