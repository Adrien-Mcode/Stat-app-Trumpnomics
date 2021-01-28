# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 11:47:55 2020

Test de stationnarité sur les données

@author: Jérémie Stym-Popper
"""
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm

from cif_OCDE import usa_bon_df

PIB_temp = usa_bon_df['PIB']

# SARIMAX
mdl = sm.tsa.statespace.SARIMAX(PIB_temp,order=(0, 0, 0),seasonal_order=(2, 2, 1, 7),enforce_stationarity=True,enforce_invertibility=True)
res = mdl.fit()
print(res.summary())

"""
# SARIMAX without seasonal_order
mdl = sm.tsa.statespace.SARIMAX(PIB_temp,order=(0, 0, 0),enforce_stationarity=True,enforce_invertibility=True)
res = mdl.fit()
print(res.summary())
"""

# Visualisation 

# fit model to data
res = sm.tsa.statespace.SARIMAX(PIB_temp,
                                order=(0, 0, 0),
                                seasonal_order=(2, 2, 1, 7),
                                enforce_stationarity=True,
                                enforce_invertibility=True).fit()
 
# in-sample-prediction and confidence bounds
pred = res.get_prediction(start = "2015-01-01", 
                          end = "2019-10-01",
                          dynamic = False, 
                          full_results=True)

# plot in-sample-prediction
fig = plt.figure(figsize=(19, 7))
ax = fig.add_subplot(111)
ax.plot(PIB_temp[0:120],color='#006699',linewidth = 3, label='Observation');
pred.predicted_mean.plot(ax=ax,linewidth = 3, linestyle='-', label='Prediction', alpha=.7, color='#ff5318', fontsize=18);
ax.set_xlabel('Années', fontsize=18)
ax.set_ylabel('PIB', fontsize=18)
plt.legend(loc='upper left', prop={'size': 20})
plt.title('Prediction ARIMA', fontsize=22, fontweight="bold")
plt.show()

rmse = math.sqrt(((pred.predicted_mean.values.reshape(-1, 1) - PIB_temp[100:120].values.reshape(-1,1)) ** 2).mean())

#### Pour afficher uniquement les résultats du test :
    # effectuer la commande suivante 

print(res.summary())
print('rmse = '+ str(rmse))

