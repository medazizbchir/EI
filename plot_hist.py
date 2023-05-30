import pandas as pd
import numpy as np

# Visualization library
import matplotlib.pyplot as plt
import altair as alt
alt.data_transformers.enable('default', max_rows=None)

# Dates management
import datetime

def hist_risk_factors(dict, df_cancer_hist, df_person_hist, df_condition_hist, nbre_patients_cancer_hist):
    
    mask = df_condition_hist.apply(tuple,1).isin(df_cancer_hist.apply(tuple,1))
    df_no_cancer_hist = df_condition_hist.loc[~mask]
    nbre_patients_no_cancer = df_no_cancer_hist.person_id.nunique()
    
    #calcul des pourcentages pour les patients atteints du cancer
    id_patients_cancer=df_cancer_hist.person_id.unique()
    df_person_cancer=df_person_hist[df_person_hist['person_id'].isin(id_patients_cancer)]
    df_person_cond_cancer=df_condition_hist.merge(df_person_cancer, on='person_id', how='inner')
    l1=[]
    for factor in dict.keys():
        df=df_person_cond_cancer[df_person_cond_cancer['condition_source_value'].isin(dict[factor])]
        l1.append(df.person_id.nunique()/nbre_patients_cancer_hist*100)

    data1 ={ 'Catégorie': list(dict.keys()),
             'Pourcentage': l1}
    
    #calcul des pourcentages pour les patients non atteints du cancer
    id_patients_no_cancer=df_no_cancer_hist.person_id.unique()
    df_person_no_cancer=df_person_hist[df_person_hist['person_id'].isin(id_patients_no_cancer)]
    df_person_cond_no_cancer=df_condition_hist.merge(df_person_no_cancer, on='person_id', how='inner')
    l2=[]
    for factor in dict.keys():
        df=df_person_cond_no_cancer[df_person_cond_no_cancer['condition_source_value'].isin(dict[factor])]
        l2.append(df.person_id.nunique()/nbre_patients_no_cancer*100)

    data2 ={ 'Catégorie': list(dict.keys()),
             'Pourcentage': l2}
    


    categories = data1['Catégorie']
    pourcentages1 = data1['Pourcentage']
    pourcentages2 = data2['Pourcentage']

    X_axis = np.arange(len(categories))
    plt.bar(X_axis - 0.2 , pourcentages1, 0.4, label='cancer')
    plt.bar(X_axis + 0.2 , pourcentages2, 0.4, label='controle')
    plt.xticks(X_axis, categories)
    plt.xlabel('Catégorie')
    plt.ylabel('Pourcentage')
    plt.title('Histogramme des facteurs de risque')
    plt.legend()
    plt.show()