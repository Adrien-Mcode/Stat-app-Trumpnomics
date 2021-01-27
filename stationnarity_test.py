# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 21:32:46 2021

Tests de stationnarité

@author: Jérémie Stym-Popper
"""

import pandas as pd
from cif_OCDE import usa_bon_df

serie1 = usa_bon_df['PIB']

# KPSS test sur la série 

from statsmodels.tsa.stattools import kpss
def kpss_test(series, **kw):    
    statistic, p_value, n_lags, critical_values = kpss(series, **kw)
    # Format Output
    print(f'KPSS Statistic: {statistic}')
    print(f'p-value: {p_value}')
    print(f'num lags: {n_lags}')
    print('Critial Values:')
    for key, value in critical_values.items():
        print(f'   {key} : {value}')
    print(f'Result: The series is {"not " if p_value < 0.05 else ""}stationary')

kpss_test(serie1)

# Le test révèle que la série n'est pas stationnaire (au seuil de 5%)

# "Stationnarisation" de la série, intégration à l'ordre 1

serie2 = serie1 - serie1.shift().fillna(0)
serie2.drop(pd.Timestamp('1990-01-01 00:00:00'), inplace=True)
kpss_test(serie2)

# Le test révèle maintenant que la série est stationnaire

# --- Visualisation de la série stationnaire

import seaborn as sns

sns.set_theme(style="darkgrid")

PIB_graph = sns.lineplot(data=serie2, x='date', y=serie2)
PIB_graph.set_title("Évolution stationnarisée du PIB américain depuis 1990")