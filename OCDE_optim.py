# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 16:36:27 2021

Travail sur la base de l'OCDE

@author: Jérémie Stym-Popper
"""

# Création d'un dataframe pour l'analyse des variables par pays

import pandas as pd

ocde_df = pd.read_csv(r"https://raw.githubusercontent.com/Adrien-Mcode/Stat-app-Trumpnomics/main/Tableaux_csv/ocde2.csv?token=ARARNIDTKBOZ6UOVAIPROP3ACR4QK")

ocde_df.rename(columns={'Unnamed: 0':'Variables'}, inplace=True)

ind_tuple = list(zip(ocde_df['Pays'], ocde_df['Variables']))
new_index = pd.MultiIndex.from_tuples(ind_tuple, names=["Pays", "Variables"])

tocde = ocde_df.T.copy()
tocde.columns = new_index
tocde.drop(['Variables', 'Pays'], inplace=True)