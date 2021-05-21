# Création d'un test d'hypothèse pour le SCM avec le space placebo

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import cvxpy as cvx
from scipy.optimize import differential_evolution, LinearConstraint
# from sklearn.model_selection import train_test_split
from random import seed

import re

seed(3)

pays_ocde = {"Germany": 'DEU', "Australia": 'AUS', "Austria": 'AUT', "Belgium": 'BEL', "Canada": 'CAN',
             "Denmark": 'DNK', "Spain": 'ESP',
             "Finland": 'FIN', "France": 'FRA', "Hungary": 'HUN', "Ireland": 'IRL', "Iceland": 'ISL', "Italy": 'ITA',
             'Korea': 'KOR',
             "Japan": 'JPN', "Luxembourg": 'LUX', "Norway": 'NOR', "New-Zealand": 'NZL', "Netherlands": 'NLD',
             "Portugal": 'PRT',
             "United Kingdom": 'GBR', "Sweden": 'SWE', "Switzerland": 'CHE', "Slovak Republic": 'SVK',
             "United-States": 'USA'}

varsg = ['PIB', 'Emplois', 'Actifs', 'Conso_share', 'Invest_share','Export_share', 'Labor_prod']
inv_map = {v: k for k, v in pays_ocde.items()}

all_w = pd.read_csv('W_pays.csv').convert_dtypes()

all_w.drop('Unnamed: 0', 1, inplace=True)

super_w = pd.DataFrame()
for pays in all_w.columns:
    i=0
    for num in all_w[pays]:
        all_w[pays][i] = (num[1:len(num)-1])
        i += 1
    super_w[pays] = all_w[pays].values.astype(float)

super_w = super_w.reindex(sorted(super_w.columns), axis=1)


pd.set_option('display.float_format', lambda x: '%.5f' % x)  # Afin de désactiver les notations exponentielles


datag = pd.read_csv('dfR_complete.csv')
datag.drop(columns=['ID_country', 'index'], inplace=True)

# Adaptation de la table pour la modélisation

df_ctg = pd.DataFrame()
for pays in pays_ocde.values():
    df_inter = pd.DataFrame()
    for var in varsg:
        concatenator = pd.DataFrame(datag[datag.LOCATION==pays].set_index('TIME')[var])
        concatenator['Variables'] = var
        concatenator.rename(columns={var:pays}, inplace=True)
        df_inter = pd.concat([df_inter, concatenator])
    df_ctg = pd.concat([df_ctg, df_inter], axis=1)

df_ctg = df_ctg.T.drop_duplicates(keep='last').T.convert_dtypes()
df_ctg.rename(columns=inv_map, inplace=True)
df_ctg.sort_index(axis=1, inplace=True)
df_ctg.drop('2020-Q1', inplace=True)

df_cho = pd.read_csv(r'donnee_chomage_Ad.csv')
df_cho = df_cho[(df_cho['LOCATION'].isin(pays_ocde.values())) &
                (df_cho['VARIABLE'] == 'UNR')].set_index(['LOCATION', 'Time'])

df_cho = df_cho.drop(['Country',
                      'VARIABLE',
                      'Variable',
                      'FREQUENCY',
                      'Frequency',
                      'TIME',
                      'Unit Code',
                      'Unit',
                      'PowerCode Code',
                      'PowerCode',
                      'Reference Period Code',
                      'Reference Period',
                      'Flag Codes',
                      'Flags'],
                     axis=1)

# Adaptation de la table pour la modélisation
df_chomage = pd.DataFrame()
for i in sorted(pays_ocde.keys()):
    interm = df_cho.loc[pays_ocde[i]]
    interm.columns = [i]
    df_chomage = pd.concat([df_chomage, interm], axis=1)

df_chomage = df_chomage.set_index(df_ctg[df_ctg.Variables=='Emplois'].index)
df_chomage.drop('United-States', 1, inplace=True)
df_chomage.drop(df_chomage[df_chomage.index>='2016-Q3'].index, inplace=True)

df_ctg.drop('United-States', 1, inplace=True)
df_ctg.drop(df_ctg[df_ctg.index>='2016-Q3'].index, inplace=True)

# Évaluation des quantités

df_ctg.Variables.unique()

W_US = pd.DataFrame(super_w['United-States']).to_numpy()
sc = df_ctg[df_ctg.Variables == 'Conso_share'].drop('Variables', 1)
(sc@W_US)[(sc@W_US).index >= '2015-Q2'].mean()

sc_cho = df_chomage@W_US
sc_cho[sc_cho.index>= '2015-Q2'].mean()

"""
pib_al.drop('Variables', 1, inplace=True)

pib_al.drop('Germany', 1)@np.matrix(super_w['Germany']).T

pib_al.drop('Germany', 1).shape
np.matrix(super_w['Germany']).T.shape


# Configuration d'un test de statistique

statistic_2 = sum([(pib_al[pays]-((pib_al.drop(pays, 1)@super_w[pays]).to_numpy()).astype(float)) for pays in super_w.columns])


[((pib_al[pays]-(pib_al.drop(pays, 1)@super_w[pays]).to_numpy()).astype(float)) for pays in super_w.columns]

np.linalg.norm
(pib_al['Germany'] - (pib_al.drop("Germany", 1)@super_w['Germany'].to_numpy()).astype(float))

pib_al.France
(pib_al.drop("France", 1)@super_w['France'].to_numpy()).astype(float)

pib_al.drop("Germany", 1)@super_w['Germany'].to_numpy() - pib_al.drop("France", 1)@super_w['France'].to_numpy()
"""
