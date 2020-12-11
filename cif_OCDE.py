# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 17:54:14 2020

Module pour importer les données de l'OCDE et visualiser le tableau

@author: Jérémie Stym-Popper
"""

from cif import cif
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

database = cif.createOneCountryDataFrameFromOECD('USA', 'MEI', 
                                     frequency='Q', startDate='1990-Q1')

usa_df = database[0]
labelvar = database[1]

#path_csv = ""
#database[1].to_csv(path_csv)
       
##--- Création d'un dataframe pour USA ----

liste_var = ['NAEXKP01', 'LREMTTTT', 'LRACTTTT', 'LRUNTTTT', 
             'NAEXKP02', 'NAEXKP04', 'NAEXKP06']

headers = ['PIB', 'Emplois', 'Actifs', 'Chomage', 'Conso', 
           'Formation', 'Exports']

d = {col:var_df for col, var_df in zip(headers, [usa_df['{0}'.format(var)]["STSA"] for var in liste_var] )}
usa_bon_df = pd.DataFrame(d)



## Créons d'abord une colonne time qui donne la date sous le format AAAA-MM-JJ

qs = usa_bon_df.index.str.replace(r'(Q\d) (\d+)', r'\2-\1')

usa_bon_df['date'] = pd.PeriodIndex(qs, freq='Q').to_timestamp()


usa_bon_df = usa_bon_df.reindex(index=usa_bon_df['date'])
usa_bon_df = usa_bon_df.drop("date", axis=1)

# path_csv = r"C:\Users\Asus\Desktop\Jérémie\Fac_ENSAE\Stat app'\Stat-app-Trumpnomics\usa_df.csv"
# usa_bon_df.to_csv(path_csv)

## ------ Stat Des -------------


sns.set_theme(style="darkgrid")

PIB_graph = sns.lineplot(data=usa_bon_df, x='date', y='PIB')
PIB_graph.set_title("Évolution du PIB américain depuis 1990")




