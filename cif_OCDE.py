# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 17:54:14 2020

Module pour importer les données de l'OCDE et visualiser le tableau

@author: Jérémie Stym-Popper
"""

import cif as cf

database = cf.createOneCountryDataFrameFromOECD('USA', 'MEI', 
                                     frequency='Q', startDate='1990-Q1')

usa_df = database[0]
labelvar = database[1]

path_csv = ""
database[1].to_csv(path_csv)
       
       