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

headers = ['PIB', 'Emplois', 'Actifs', 'Chomage', 'Conso', 'Formation',
           'Exports']

missing_countries = pd.DataFrame(columns = headers.append('Pays'))

liste_var = ['NAEXKP01', 'LREMTTTT', 'LRACTTTT', 'LRUNTTTT', 'NAEXKP02',
             'NAEXKP04', 'NAEXKP06']


pays_ocde2 = {'Korea': 'KOR', 'Hungary': 'HUN', 'Slovak Republic': 'SVK',
             'Iceland': 'ISL'}

pays_ocde = {"Germany" :'DEU',"Australia" :'AUS',"Austria":'AUT',"Belgium":'BEL',"Canada":'CAN',"Denmark":'DNK',"Spain":'ESP',"Finland":'FIN',"France":'FRA',"Greece":'GRC',"Ireland":'IRL',"Italy":'ITA',
             "Japan":'JPN',"Luxembourg":'LUX',"Norway":'NOR',"New-Zealand":'NZL',"Netherlands":'NLD',"Portugal":'PRT',"United Kingdom":'GBR',"Sweden":'SWE',"Switzerland":'CHE',"Turkey":'TUR',"United-States":'USA'}


#Note : dans les pays de l'OCDE ici on prend le royaume uni, mais le code laissé est celui de la grande bretagne. C'est une irrégularité dans les données, pour l'instant j'utilise la solution de facilité 
#car plus tard on a des données uniquement sur le Royaume Uni (les données de la world inequality database)

for country in pays_ocde2.keys():
    # On importe de l'OCDE les données :
    country_df = cif.createOneCountryDataFrameFromOECD('{0}'.format(pays_ocde2[country]),
                                                       'MEI', frequency='Q',
                                                       startDate='1990-Q1',
                                                       endDate = '2019-Q4')[0]
    
    #On récupère les colonnes:
    d = {col:var_df for col, var_df in zip(headers, [country_df['{0}'.format(var)]["STSA"] for var in liste_var])}
    country_bon_df = pd.DataFrame(d)
    
    qs = country_bon_df.index.str.replace(r'(Q\d) (\d+)', r'\2-\1')
    country_bon_df = country_bon_df.T
    country_bon_df.columns = qs
    country_bon_df['Pays'] = pays_ocde2['{0}'.format(str(country))]
    missing_countries = pd.concat([missing_countries, country_bon_df], axis=0)

missing_countries = missing_countries.reset_index()
missing_countries.rename(columns={'index': 'Variables'}, inplace=True)
missing_countries.columns = list(missing_countries.columns) # Supprime "time"


ind_tuple = list(zip(missing_countries['Pays'], missing_countries['Variables']))
new_index = pd.MultiIndex.from_tuples(ind_tuple, names=["Pays", "Variables"])

tocde2 = missing_countries.T.copy()
tocde2.columns = new_index
tocde2.drop(['Variables', 'Pays'], inplace=True)

ocde_df = pd.read_csv("Tableaux_csv/ocde2.csv")

ocde_df.rename(columns={'Unnamed: 0':'Variables'}, inplace=True)

ind_tuple = list(zip(ocde_df['Pays'], ocde_df['Variables']))
new_index = pd.MultiIndex.from_tuples(ind_tuple, names=["Pays", "Variables"])

tocde = ocde_df.T.copy()
tocde.columns = new_index
tocde.drop(['Variables', 'Pays'], inplace=True)

df_allcountries = pd.concat([tocde, tocde2], 1)

# df_allcountries.to_csv(r"C:\Users\Asus\Desktop\Jérémie\Fac_ENSAE\Stat app'\Stat-app-Trumpnomics\df_allcountries.csv")