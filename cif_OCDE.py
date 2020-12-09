# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 17:54:14 2020

Module pour importer les données de l'OCDE et visualiser le tableau

@author: Jérémie Stym-Popper
"""

from cif import cif
import pandas as pd

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