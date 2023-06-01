import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import altair as alt
alt.data_transformers.enable('default', max_rows=None)

import datetime

cancer_condition = {'C50','C500','C501','C502','C503','C504'}
risk_factors = {'tabac':['Z587','Z720'], 'alcool':['T51','K70','F10'], 'diabete':['E10','E11','E12'], 'sub_psy':['Z864'], 'tum_herit':['Z803']}

df_person = pd.read_pickle('data/df_person.pkl')
df_visit = pd.read_pickle('data/df_visit.pkl')
df_condition = pd.read_pickle('data/df_condition.pkl')
df_dedup_proba = pd.read_pickle('data/df_dedup_proba.pkl')

df_person['gender_source_value'] = df_person['gender_source_value'].replace(['female', 'f'], 'f')
df_person['gender_source_value'] = df_person['gender_source_value'].replace(['male', 'm'], 'm')

def deduplicate_proba(df_person: pd.DataFrame, df_dedup_proba: pd.DataFrame, score: int):
    #Only keep rows with a probability above the value score
    df_dedup_proba_score = df_dedup_proba[df_dedup_proba['prob'] > score]
    # Outer Join
    df_person_dedup_proba  = pd.merge(df_person, df_dedup_proba_score, on = 'person_id', how = 'outer')
    # Only unique ids in unique_person_id
    df_person_dedup_proba['unique_person_id'] = df_person_dedup_proba['unique_person_id'].fillna(df_person_dedup_proba['person_id'])
    # Only keep one row per patient
    df_person_dedup_proba = df_person_dedup_proba.drop_duplicates(['unique_person_id'], keep = 'first')
    return df_person_dedup_proba

df_person_dedup_proba = deduplicate_proba(df_person, df_dedup_proba, score=0.90)
df_condition_dedup_proba = df_condition.merge(df_person_dedup_proba[['person_id']], on='person_id', how='inner')
df_visit_dedup_proba = df_visit.merge(df_person_dedup_proba[['person_id']], on='person_id', how='inner')
df_cancer_dedup_proba = df_condition_dedup_proba[df_condition_dedup_proba['condition_source_value'].isin(cancer_condition)]
nbre_patients_cancer_dedup_proba = df_cancer_dedup_proba.person_id.nunique()