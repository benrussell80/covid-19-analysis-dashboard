import json
import pickle
import pandas as pd
import os
from utils import join_to_data_folder

def main():
    HERE = os.path.dirname(__file__)

    filename = 'COVID19_line_list_data.csv'
    df = pd.read_csv(join_to_data_folder('raw', filename))

    # Convert dtypes (consider switching to `infer_dtypes`)
    df['gender'] = df.gender.astype('category')
    df['recovered_date'] = pd.to_datetime(df.recovered, errors='coerce')
    df['recovered'] = df.recovered.apply(lambda value: False if value == '0' else True)
    df['death_date'] = pd.to_datetime(df.death, errors='coerce')
    df['death'] = df['death'].apply(lambda value: False if value == '0' else True)
    df['hospital_visit_date'] = pd.to_datetime(df.hosp_visit_date)
    df['onset_approximated'] = df['If_onset_approximated'].astype(bool)
    df['exposure_start'] = pd.to_datetime(df.exposure_start)
    df['exposure_end'] = pd.to_datetime(df.exposure_end)
    df['visiting_wuhan'] = df['visiting Wuhan'].astype(bool)
    df['symptom_onset'] = pd.to_datetime(df.symptom_onset)
    df['age'] = df.age.astype(float)
    df['reporting_date'] = pd.to_datetime(df['reporting date'])
    df['from_wuhan'] = df['from Wuhan'].astype(bool)
    df['country'] = df['country'].astype('category')

    df.rename(columns={'symptom': 'symptoms'}, inplace=True)

    df.drop([
        'id', *[col for col in df.columns if col.startswith('Unnamed:')],
        'If_onset_approximated', 'hosp_visit_date',
        'visiting Wuhan', 'from Wuhan', 'reporting date'
    ], inplace=True, axis=1)

    # Process symptoms
    unique_symptoms = set(pd.get_dummies(df.symptoms.str.split(', ').apply(pd.Series).T, prefix='', prefix_sep='').columns)

    try:
        with open(os.path.join(HERE, 'possible_symptoms.txt'), 'r') as fh:
            possible_symptoms = fh.read().split('\n')
    except FileNotFoundError:
        possible_symptoms = [
            'abdominal pain', 'shortness of breath', 'chest pain', 
            'chills', 'cough', 'diarrhea', 'fatigue', 'fever',
            'flu like symptoms', 'headache', 'sore throat', 'joint pain',
            'loss of appetite', 'muscle aches', 'nausea', 'runny nose',
            'pneumonia', 'reflux', 'thirst', 'vomiting'
        ]
        
    try:
        with open(os.path.join(HERE, 'symptom_map.json'), 'r') as fh:
            symptom_map = json.load(fh)
    except FileNotFoundError:
        symptom_map = {
            'aching muscles': 'muscle aches', 'abdominal pain': 'abdominal pain',
            'short of breath': 'shortness of breath', 'breathlessness': 'shortness of breath',
            'difficulty breathing': 'shortness of breath', 'difficult in breathing': 'shortness of breath',
            'dyspnea': 'shortness of breath', 'shortness of breath': 'shortness of breath',
            'chest discomfort': 'chest pain', 'chest pain': 'chest pain',
            'chill': 'chills', 'chills': 'chills',
            'cold': 'cold', 'coughing': 'cough',
            'cough with sputum': 'cough', 'mild cough': 'cough',
            'sputum': 'cough', 'respiratory distress': 'cough',
            'cough': 'cough', 'diarrhea': 'diarrhea',
            'tired': 'fatigue', 'tiredness': 'fatigue',
            'sluggishness': 'fatigue', 'malaise': 'headache',
            'physical discomfort': 'fatigue', 'fatigue': 'fatigue',
            'feaver': 'fever', 'feve\\': 'fever',
            'high fever': 'fever', 'mild fever': 'fever',
            'fever': 'fever', 'flu': 'flu-like symptoms',
            'flu symptoms': 'flu-like symptoms', 'flu-like symptoms': 'flu-like symptoms',
            'heavy head': 'headache', 'headache': 'headache',
            'itchy throat': 'sore throat', 'throat discomfort': 'sore throat',
            'throat pain': 'sore throat', 'sore throat': 'sore throat',
            'joint pain': 'joint pain', 'loss of appetite': 'loss of appetite',
            'muscle cramps': 'muscle aches', 'muscle pain': 'muscle aches',
            'myalgia': 'muscle aches', 'myalgias': 'muscle aches',
            'sore body': 'muscle aches', 'muscle aches': 'muscle aches',
            'nausea': 'nausea', 'nasal discharge': 'runny nose',
            'runny nose': 'runny nose', 'sneeze': 'runny nose',
            'pneumonia': 'pneumonia', 'reflux': 'reflux',
            'thirsty': 'thirst', 'thirst': 'thirst', 'vomiting': 'vomiting'
        }
        
    for symptom in unique_symptoms:
        if symptom not in symptom_map:
            print('\n\t- '.join(['Options:', *possible_symptoms]))
            print(f'"{symptom}" does not have a known alias.')
            alias = input(f'Enter alias for "{symptom}": ')
            if alias not in possible_symptoms:
                possible_symptoms.append(alias)
            symptom_map[alias] = symptom
            
    with open(os.path.join(HERE, 'symptom_map.json'), 'w') as fh:
        json.dump(symptom_map, fh, indent=4)
        
    with open(os.path.join(HERE, 'possible_symptoms.txt'), 'w') as fh:
        fh.write('\n'.join(possible_symptoms))

    for symptom in possible_symptoms:
        df[f"experienced_{symptom.replace(' ', '_')}"] = df.symptoms.str.split(', ').apply(
            lambda value: pd.NA if isinstance(value, float) else True if symptom in [symptom_map[item] for item in value] else False
        )

    df['symptom_onset_delay'] = (df['symptom_onset'] - df['exposure_start']).dt.days

    df.to_csv(join_to_data_folder('cleaned', filename), index=False)


if __name__ == "__main__":
    main()