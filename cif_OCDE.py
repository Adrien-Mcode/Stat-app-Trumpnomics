# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 17:54:14 2020

Module pour importer les données de l'OCDE et visualiser le tableau

@author: Jérémie Stym-Popper
"""

import cif


createOneCountryDataFrameFromOECD('USA', 'MEI',
                                      frequency='Q', startdate='1990-Q1')