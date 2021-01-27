# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 21:32:46 2021

Tests de stationnarité

@author: Jérémie Stym-Popper
"""

from cif_OCDE import usa_bon_df

serie1 = usa_bon_df['PIB'].values

# KPSS test
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
