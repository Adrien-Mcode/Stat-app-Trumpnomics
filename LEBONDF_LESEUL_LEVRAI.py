# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 17:03:47 2021

Correction de la table ocde_df pour le donor pool

@author: Jérémie Stym-Popper
"""

from cif import cif
import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np




headers = ['PIB', 'Emplois', 'Actifs', 'Chomage', 'Conso', 'Formation', 'Exports']
ocde_df = pd.DataFrame(columns = headers.append('Pays'))

liste_var = ['NAEXKP01', 'LFEMTTTT', 'LFACTTTT', 'LRUNTTTT', 'NAEXKP02', 'NAEXKP04', 'NAEXKP06']



pays_ocde = {"Germany" :'DEU',"Australia" :'AUS',"Austria":'AUT',"Belgium":'BEL',"Canada":'CAN',"Denmark":'DNK',"Spain":'ESP',
             "Finland":'FIN',"France":'FRA',"Hungary":'HUN',"Ireland":'IRL', "Iceland": 'ISL', "Italy":'ITA', 'Korea': 'KOR',
             "Japan":'JPN',"Luxembourg":'LUX',"Norway":'NOR',"New-Zealand":'NZL',"Netherlands":'NLD',"Portugal":'PRT',
             "United Kingdom":'GBR',"Sweden":'SWE',"Switzerland":'CHE',"Slovak Republic":'SVK',"United-States":'USA'}
#Note : dans les pays de l'OCDE ici on prend le royaume uni, mais le code laissé est celui de la grande bretagne. C'est une irrégularité dans les données, pour l'instant j'utilise la solution de facilité 
#car plus tard on a des données uniquement sur le Royaume Uni (les données de la world inequality database)

for country in pays_ocde.keys():
    # On importe de l'OCDE les données :
    country_df = cif.createOneCountryDataFrameFromOECD('{0}'.format(pays_ocde[country]),
                                                       'MEI', frequency='Q',
                                                       startDate='1990-Q1',
                                                       endDate = '2019-Q4')[0]
    
    #On récupère les colonnes:
    d = {col:var_df for col, var_df in zip(headers, [country_df['{0}'.format(var)]["STSA"] for var in liste_var])}
    country_bon_df = pd.DataFrame(d)
    
    # qs = country_bon_df.index.str.replace(r'(Q\d) (\d+)', r'\2-\1')
    country_bon_df = country_bon_df.T
    # country_bon_df.columns = qs
    country_bon_df['Pays'] = country
    ocde_df = pd.concat([ocde_df, country_bon_df], axis=0)

ocde_df = ocde_df.reset_index()
ocde_df.rename(columns={'index': 'Variables'}, inplace=True)
ocde_df.columns = list(ocde_df.columns) # Supprime "time"


ind_tuple = list(zip(ocde_df['Pays'], ocde_df['Variables']))
new_index = pd.MultiIndex.from_tuples(ind_tuple, names=["Pays", "Variables"])

df_countries = ocde_df.T.copy()
df_countries.columns = new_index
df_countries.drop(['Variables', 'Pays'], inplace=True)


# df_countries.to_csv(r"C:\Users\Asus\Desktop\Jérémie\Fac_ENSAE\Stat app'\Stat-app-Trumpnomics\df_countries.csv")