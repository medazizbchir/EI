# Final project

## Introduction

This project mimics an end-to-end study conducted on a clinical data warehouse and leading to the publication of a scientific article.

## Study design

Leveraging real world data collected in the AP-HP Hospitals and centralized in its clinical data warehouse, 
you will realize an end-to-end study to identify in the literature potential risk factors associated with breast cancer, and confront them to the available features in your database. You will need to perform biostatistical analyses to quantify the impact of each risk factors, and finally sum up your results in a brief article.
We consider data that has been extracted on $t_{extract}=$ December 1st, 2025.

The study will be composed of the following steps:  
- **Literature review**: check in the literature the different risk factors identified and tested by the scientific community that you could confront to your own database (and register those not available for further studies/data integration)  
- **Data pre-processing**:  
  - **Data cleaning** (identity deduplication, date cleaning, etc.)  
  - **Variable extraction** (risk factors, cancer outcomes). Cancer outcomes will be defined using claim codes (condition data) attached to each visit. Smoking risk factor may be defined using either claim codes, or by leveraging a new rule-based NLP algorithm. Other comorbidities should be extracted using their associated ICD-10 codes. Biological values may be used as is.  
- **Statistical analysis**  
  - **Statistical Group Comparison**: Compare the features' distribution between groups, and check the significativity of your results.  
  - **Biostatistics**: implement univariate and multivariate regression, or any other model you might find interesting for the study.  
  - **Sensitivity analysis**: assess whether the results are robust to alternative parameterization of the analysis pipeline  

## Deliverables
In this project, we expect a twofolds reporting of the study. First, a brief scientific article shall present the literature review conclusion, the study design, its results and discuss them. Second, the computer code used to realize the analysis shall be delivered to evaluators in order to ensure study reproducibility.