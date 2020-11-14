# COVID-19 Analysis Dashboard
## Description
A comprehensive analysis of COVID-19 data created using Bokeh from Python. Analysis includes
- Geographic representations of virus spread
- Summaries of line list data
- Age/Gender groupings
- Logistic growth fitting and forecasting of number of total cases in each country

## Data Source
[Kaggle](https://www.kaggle.com/sudalairajkumar/novel-corona-virus-2019-dataset#time_series_covid_19_deaths.csv)

## Site
https://covid19bokehapp.herokuapp.com

## Installation
Developed with python 3.8, bokeh 2.0

    git clone https://github.com/benrussell80/covid-19-analysis-dashboard
    cd covid-19-analysis-dashboard
    pip install -r requirements.txt
    # download newest data and unzip it to the raw data folder
    kaggle datasets download sudalairajkumar/novel-corona-virus-2019-dataset
    unzip novel-corona-virus-2019-dataset.zip -d bokeh_app/data/raw/
    # clean the data
    python bokeh_app/scripts/run_all_cleaning_and_analysis_scripts.py 
    bokeh serve bokeh_app/
<!--
## To Do
Add instructions to each tab
### Tab 1 - World Map
- [ ] Deaths, death rates
- [ ] Change circles to country-shaped polygons
### Tab 2 (hidden on site) - United States Map
- [ ] Speed up sliding; decrease number of counties shown; group by states
- [ ] Deaths, death rates
- [ ] Change circles to country-shaped polygons
### Tab 3 - World Cases Time Series
- [ ] Filters for continent
### Tab 4 - United States Time Series
- [ ] Filters for state
### Tab 5 - Case Details
- [ ] Add filters to limit data (e.g. age double sliders, country selector, etc.)
- [ ] Button for downloading data
- [ ] Formatters for Boolean data, etc.
### Tab 6 - Analysis
- [x] World Fitting to logistic function
- [x] US Fitting to logistic function (fix script to match world fitting)
- [x] Hover tool for displaying projected maximum
- [x] Fill between 9X% confidence interval (changing L)
- [x] Country selector for world projections
- [ ] Choose confidence level (RadioButton)
- [ ] Quick facts tab (average time between exposure and symptom onset, most common symptoms, death rates by age)
- [ ] Symptom tab
- [ ] Death rates by age, gender, symptoms, country, length of sickness, US region
- [ ] Average time between exposure and symptom onset
-->
