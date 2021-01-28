# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 12:02:04 2020

Stats descriptives : comparaison des PIB OCDE

@author: Jérémie Stym-Popper
"""

import pandas as pd
from cif import cif
from cif_OCDE import usa_bon_df
import seaborn as sns
import matplotlib.pyplot as plt

compare_df = pd.DataFrame(usa_bon_df['PIB'])
compare_df = compare_df.rename(columns={'PIB':'USA'})

liste_var = ['NAEXKP01', 'LREMTTTT', 'LRACTTTT', 'LRUNTTTT', 
             'NAEXKP02', 'NAEXKP04', 'NAEXKP06']

headers = ['PIB', 'Emplois', 'Actifs', 'Chomage', 'Conso', 
           'Formation', 'Exports']

for country in ['FRA', 'ITA', 'BEL', 'DEU', 'CAN', 'AUS', 'GBR', 'JPN']:
        
    
    country_df = cif.createOneCountryDataFrameFromOECD('{0}'.format(country),
                                                       'MEI', frequency='Q',
                                                       startDate='1990-Q1')[0]
    
    
    d = {col:var_df for col, var_df in zip(headers, [country_df['{0}'.format(var)]["STSA"] for var in liste_var])}
    country_bon_df = pd.DataFrame(d)
    
    qs = country_bon_df.index.str.replace(r'(Q\d) (\d+)', r'\2-\1')
    country_bon_df['date'] = pd.PeriodIndex(qs, freq='Q').to_timestamp()
    country_bon_df = country_bon_df.reindex(index=country_bon_df['date'])
    country_bon_df = country_bon_df.drop("date", axis=1)
    
    compare_df = pd.concat([compare_df, country_bon_df.rename(columns={'PIB':'{0}'.format(country)})['{0}'.format(country)]], axis=1)

##`--- Conversion des monnais nationales en dollars
compare_df['JPN'] = compare_df['JPN']*0.0096
compare_df['FRA'] = compare_df['FRA']*1.22
compare_df['DEU'] = compare_df['DEU']*1.22
compare_df['ITA'] = compare_df['ITA']*1.22
compare_df['BEL'] = compare_df['BEL']*1.22
compare_df['CAN'] = compare_df['CAN']*0.79
compare_df['GBR'] = compare_df['GBR']*1.34
compare_df['AUS'] = compare_df['AUS']*0.76


## ------ Visualisation ---------

compare_df['FRA'].plot(label='France')
compare_df['DEU'].plot(label='Allemagne')
compare_df['JPN'].plot(label='Japon')
compare_df['ITA'].plot(label='Italie')
compare_df['GBR'].plot(label="Grande Bretagne")
compare_df['CAN'].plot(label='Canada')
plt.title("PIB de certains pays de l'OCDE")
plt.legend(loc='best')
plt.show()

