# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 23:58:34 2021

Rajout et preprocessing du df_chomage

@author: Jérémie Stym-Popper
"""

import pandas as pd

pays_ocde = {"Germany" :'DEU',"Australia" :'AUS',"Austria":'AUT',"Belgium":'BEL',"Canada":'CAN',"Denmark":'DNK',"Spain":'ESP',
             "Finland":'FIN',"France":'FRA',"Hungary":'HUN',"Ireland":'IRL', "Iceland": 'ISL', "Italy":'ITA', 'Korea': 'KOR',
             "Japan":'JPN',"Luxembourg":'LUX',"Norway":'NOR',"New-Zealand":'NZL',"Netherlands":'NLD',"Portugal":'PRT',
             "United Kingdom":'GBR',"Sweden":'SWE',"Switzerland":'CHE',"Slovak Republic":'SVK',"United-States":'USA'}

df_chomage = pd.read_csv('df_chomage.csv')

df_chomage = df_chomage[['TIME', 'LOCATION', 'Value']]
df_chomage = df_chomage[df_chomage['LOCATION'].isin(pays_ocde.values())]

df_chomage = df_chomage[df_chomage.TIME <'2020-Q1']
df_chomage = df_chomage.set_index(df_chomage.TIME).drop('TIME', 1)

chomage_ct = pd.DataFrame()
for pays in pays_ocde.values():
    chomage_ct = pd.concat([chomage_ct, df_chomage[df_chomage.LOCATION==pays].Value], 1)
    
chomage_ct.columns = pays_ocde.keys()
chomage_ct.sort_index(inplace=True)
chomage_ct.dropna(inplace=True)
