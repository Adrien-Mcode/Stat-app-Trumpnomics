# -*- coding: utf-8 -*-
"""
Created on Sat Mar 20 17:45:52 2021
Sauvegarde du contrôle synthétique propre
@author: Jérémie Stym-Popper
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 22:51:14 2021
@author: SURFACE
"""

# Mise au propre du code de test controle synth :

# ------------ Importation des modules et fixation de l'aléatoire ---------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import cvxpy as cvx
from scipy.optimize import differential_evolution, LinearConstraint
# from sklearn.model_selection import train_test_split
from random import seed

#%matplotlib inline

seed(3)

# ------------ Importation des données et traitement de celles-ci ---------------

pays_ocde = {"Germany": 'DEU', "Australia": 'AUS', "Austria": 'AUT', "Belgium": 'BEL', "Canada": 'CAN',
             "Denmark": 'DNK', "Spain": 'ESP',
             "Finland": 'FIN', "France": 'FRA', "Hungary": 'HUN', "Ireland": 'IRL', "Iceland": 'ISL', "Italy": 'ITA',
             'Korea': 'KOR',
             "Japan": 'JPN', "Luxembourg": 'LUX', "Norway": 'NOR', "New-Zealand": 'NZL', "Netherlands": 'NLD',
             "Portugal": 'PRT',
             "United Kingdom": 'GBR', "Sweden": 'SWE', "Switzerland": 'CHE', "Slovak Republic": 'SVK',
             "United-States": 'USA'}

# Dictionnaire qui inverse clés et valeurs du précédent, pour la table df_ctg
inv_map = {v: k for k, v in pays_ocde.items()}

variables = ['Actifs', 'Emplois', 'PIB']

# Les variables qu'on utilisera pour la modélisation
# Conso_share : la part de la consomation en % dans le PIB
# Invest_share : idem pour l'investissement
# Export_share : idem pour les exportations
# Labor_prod : la productivité du travail

varsg = ['PIB', 'Emplois', 'Actifs', 'Conso_share', 'Invest_share','Export_share', 'Labor_prod']

# Ajout des données sur le chômage plus complète

df_cho = pd.read_csv(r'donnee_chomage_Ad.csv')
df_cho = df_cho[(df_cho['LOCATION'].isin(pays_ocde.values())) &
                (df_cho['VARIABLE'] == 'UNR')].set_index(['LOCATION', 'Time'])

df_cho = df_cho.drop(['Country',
                      'VARIABLE',
                      'Variable',
                      'FREQUENCY',
                      'Frequency',
                      'TIME',
                      'Unit Code',
                      'Unit',
                      'PowerCode Code',
                      'PowerCode',
                      'Reference Period Code',
                      'Reference Period',
                      'Flag Codes',
                      'Flags'],
                     axis=1)

# Adaptation de la table pour la modélisation
df_chomage = pd.DataFrame()
for i in sorted(pays_ocde.keys()):
    interm = df_cho.loc[pays_ocde[i]]
    interm.columns = [i]
    df_chomage = pd.concat([df_chomage, interm], axis=1)


'''
#Les auteurs précisent qu'ils prennent comme critère de validation la qualité de la modélisation sur le taux de chomage.
#On créé donc un df contenant tous les taux de chomage
df_chomage = data.xs('Chomage',axis = 1,level = 1,drop_level = True).drop(list(data.reset_index().loc[d,'Pays'][0] for d in range(88,99)))
#Note : on a une problème de valeurs manquantes sur ce df, pour l'instant on utilise donc
#la fonction df.fillna() qui les remplacent par des 0, mais il faudra voir pour à terme
#faire autre chose avec :
df_chomage = df_chomage.dropna()
'''

# Voici une nouvelle base de données avec toutes les variables et sans données manquantes

datag = pd.read_csv('dfR_complete.csv')
datag.drop(columns=['ID_country', 'index'], inplace=True)

# Adaptation de la table pour la modélisation

df_ctg = pd.DataFrame()
for pays in pays_ocde.values():
    df_inter = pd.DataFrame()
    for var in varsg:
        concatenator = pd.DataFrame(datag[datag.LOCATION==pays].set_index('TIME')[var])
        concatenator['Variables'] = var
        concatenator.rename(columns={var:pays}, inplace=True)
        df_inter = pd.concat([df_inter, concatenator])
    df_ctg = pd.concat([df_ctg, df_inter], axis=1)

df_ctg = df_ctg.T.drop_duplicates(keep='last').T.convert_dtypes()
df_ctg.rename(columns=inv_map, inplace=True)
df_ctg.sort_index(axis=1, inplace=True)
df_ctg.drop('2020-Q1', inplace=True)

# De la table précédente nous créons deux tables :
# - df_fit qui donne les séries temporelles pour la modélisation
# - df_meaner qui donne les valeurs sur lesquelles calculer les moyennes
# (les 5 valeurs en plus que nous rajoutons pour la régression)

df_fit = df_ctg[df_ctg.Variables.isin(['PIB', 'Emplois', 'Actifs'])]
df_meaner = df_ctg[df_ctg.Variables.isin(['Conso_share', 'Invest_share',
                                          'Export_share', 'Labor_prod'])]
df_chomage.set_index(df_ctg[df_ctg.Variables=='PIB'].index, inplace=True)
df_chomage['Variables'] = 'Chomage'

df_meaner = pd.concat([df_meaner, df_chomage]).convert_dtypes()

# ------------ Partie Modélisation ----------------------------------------------

# Afin de rendre les sorties plus lisibles, on supprime les notations exponentielles.
np.set_printoptions(suppress=True)

# On créé le problème d'optimisation cvxpy :

# On prépare le vecteur qui contient les valeurs qui nous intéressent pour les USA :

X1 = df_fit[['United-States', 'Variables']]
X1 = X1.drop(X1[X1.index>='2017-Q1'].index) # Suppression des données post élections
X1_mean = df_meaner[['United-States', 'Variables']].groupby('Variables').mean()
X1 = pd.concat([X1, X1_mean]).reset_index().drop(['index', 'Variables'], 1)
X1 = X1.values.astype(float) # S'assurer que les données sont bien numériques

# On prépare le vecteur qui contient les valeurs qui nous intéressent pour les autres pays :

X0 = df_fit.drop('United-States', 1)
X0 = X0.drop(X0[X0.index>='2017-Q1'].index)
X0_mean = df_meaner.drop('United-States', 1).groupby('Variables').mean()
X0 = pd.concat([X0, X0_mean]).reset_index().drop(['index', 'Variables'], 1)
X0 = X0.values.astype(float)

# On construit le problème cvxpy
V_opt = cvx.Parameter((269, 269), PSD=True)  # On définit V qui est un vecteur de paramètre
x = cvx.Variable((24, 1), nonneg=True)  # On définit un vecteur de variables cvxpy

# On définit la fonction de cout : norme des résidus
cost = cvx.pnorm(V_opt @ (X1 - X0 @ x))
constraints = [cvx.sum(x) == 1]  # La contrainte
prob = cvx.Problem(cvx.Minimize(cost), constraints)  # On définit le problème


# On définit une fonction qui renvoit le "cout" pour l'optimisation de la fonction V :
def loss_V(V,pays=('United-states')):
    V_opt.value = np.diag(np.abs(V) ** 1 / 2)
    prob.solve(warm_start=True)
    return (np.linalg.norm(
        (df_chomage[pays[0]].values - df_chomage.drop(pays[0], axis=1).values @ x.value)))


# Note de performance : utiliser la fonction pnorm plutot que quadform est plus avantageux (de peu, on gagne environ 8 minutes sur le temps d'éxecution total)

# On définit et résout le problème d'optimisation en V :

contrainte = LinearConstraint(np.ones((1, 269)), 1, 1)
bounds = [(0, 1) for i in range(269)]
result = differential_evolution(loss_V, bounds, maxiter=1, constraints=contrainte, polish=False)

V_opt.value = np.diag(result.x)

# On "réinjecte" la matrice V_opt dans le problème d'optimisation, avec ses valeures optimales
cost = cvx.pnorm(V_opt.value @ (X1 - X0 @ x))
prob = cvx.Problem(cvx.Minimize(cost), constraints)  # On définit le problème

prob.solve()
W = x.value
RMSPE = np.linalg.norm((X1 - X0 @ W))


# ------------ Affichage des Résultats ------------------------------------------

# Voici la table des coefficients attribués à chaque pays
pd.set_option('display.float_format', lambda x: '%.3f' % x)  # Afin de désactiver les notations exponentielles

# Affichage de la table des coefficients :
country_list = df_fit.drop(['United-States', 'Variables'], axis=1)
coeff = pd.DataFrame(x.value, index=country_list.columns)
print(coeff)

# Commençons par visualiser l'écart de tendance en PIB
df_pib = df_fit[df_fit["Variables"] == "PIB"]

# Cette table va nous servir plus tard pour automatiser la modélisation

# Création du contrôle synthétique comme somme pondérée des autres pays
sc = df_pib.drop(['Variables', 'United-States'], axis=1) @ W

(df_pib['United-States']*100).plot()
plt.plot(sc.values*100, label="Synthetic Control")
plt.vlines(84, 0, 100, linestyle='--', color='red', label='Election de Trump')
plt.legend()
plt.show()
plt.close()

# On peut visualiser l'écart en terme de taux de chômage :

df_chomage['United-States'].plot(label="États-Unis")
plt.plot(df_chomage.drop(['United-States','Variables'], axis=1).values @ W, label="Contrôle Synthétique")
plt.legend()
plt.show()
plt.close()


# ------------ Partie passage en fonction : -------------------------------------


def liste_date(date = [2017,2019]):
    '''
    Crée une liste de date au bon format pour le retirer des données
    Par exemple, on retire toutes les dates postérieures à l'élection pour le
    contrôle synthétique.
    On systématise ce retrait pour les time-placebos
    '''
    liste_d = []
    for i in range(date[0], date[1] + 1):
        for j in range(1, 5):
            liste_d.append(str(i) + '-Q' + str(j))
    return(liste_d)


def prep_donnee(pays, date=[2017,2019], placebo=False):
    '''
    Une fonction qui exécute automatiquement le preprocessing pour les données
    avant modélisation du contrôle synthétique.
    '''
    X1 = df_fit[[pays, 'Variables']]
    if placebo :
        X1 = X1.drop(date)
    else:
        X1 = X1.drop(liste_date(date))
    #X1 = X1.drop(list(data.reset_index().loc[d, 'Pays'][0] for d in range(88, 99)))
    X1_mean = df_meaner[[pays, 'Variables']].groupby('Variables').mean().reset_index()
    X1 = pd.concat([X1, X1_mean]).reset_index().drop(['index', 'Variables'], 1)
    X1 = X1.values.astype(float)

    X0 = df_fit.drop(pays, 1)
    if placebo :
        X0 = X0.drop(date)
    else:
        X0 = X0.drop(liste_date(date))
    #X0 = X0.drop(list(data.reset_index().loc[d, 'Pays'][0] for d in range(88, 99)))
    X0_mean = df_meaner.drop(pays, 1).groupby('Variables').mean().reset_index()
    X0 = pd.concat([X0, X0_mean]).reset_index().drop(['index', 'Variables'], 1)
    X0 = X0.values.astype(float)

    return (X1, X0)


def synth(X1, X0,pays='United-States'):
    """
    Fonction qui automatise le contrôle synthétque sur un pays donnée.
    Il faut que les données soient pré-traitées ! cf. prep_donnee()
    """
    V_opt = cvx.Parameter((X0.shape[0], X0.shape[0]), PSD=True)  # On définit V qui est un vecteur de paramètre
    x = cvx.Variable((X0.shape[1], 1), nonneg=True)  # On définit un vecteur de variables cvxpy
    cost = cvx.pnorm(V_opt @ (X1 - X0 @ x))  # On définit la fonction de cout : norme des résidus
    constraints = [cvx.sum(x) == 1]  # La contrainte
    prob = cvx.Problem(cvx.Minimize(cost), constraints)  # On définit le problème

    # tps1 = clock()

    contrainte = LinearConstraint(np.ones((1,X0.shape[0])), 1, 1)
    bounds = [(0, 1) for i in range(X0.shape[0])]
    result = differential_evolution(loss_V,bounds,args=(pays),maxiter=10, constraints=contrainte, polish=False)

    # tps2 = clock()
    # print((tps2 - tps1)/60)

    V_opt.value = np.diag(result.x)
    cost = cvx.pnorm(V_opt.value @ (X1 - X0 @ x))
    prob = cvx.Problem(cvx.Minimize(cost), constraints)
    prob.solve()
    W = x.value
    RMSPE_train = np.linalg.norm((X1 - X0 @ W))
    return W, V_opt.value, RMSPE_train


def synth_plot(W, pays='United-States'):
    """
    Une fois obtenue le vecteur W de pondération, on peut afficher les courbes
    du contrôle synthétique sur le PIB et le chômage.
    Affichage des intervalles de confiance en zone grisée.
    L'intervalle de confiance correspond à + et - l'écart type autour de la
    courbe du contrôle synthétique.
    L'écart type est celui de la série différenciée entre le contrôle synthétique
    et la vraie valeur de la série temporelle (ex: PIB_USA - PIB_SC).
    """
    sc_pib = df_pib.drop(['Variables', pays], axis=1) @ W
    error = (np.array(df_pib[pays].values) - sc_pib.values.astype(float).reshape(100)).std()

    fig1 = plt.figure(0)

    (df_pib[pays]*100).plot()
    plt.plot(sc_pib.values*100, label="Synthetic Control")
    plt.vlines(84, 0, 100, linestyle='--', color='red', label='Election de Trump')


    plt.title('Graphique du PIB : {0}'.format(pays))
    plt.xlabel('Années')
    plt.ylabel('Écart du PIB par rapport à 1995 en pourcentage')
    plt.fill_between(df_pib.index,
        np.array((sc_pib.values - 2*error).reshape(100) * 100, dtype=float),
        np.array((sc_pib.values + 2*error).reshape(100) * 100, dtype=float),
        color='0.75')
    plt.legend()
    plt.show()
    #plt.close()


    sc_chomage = df_chomage.drop([pays,'Variables'], axis=1).values @ W
    error = (np.array(df_chomage[pays].values) - sc_chomage.astype(float).reshape(100)).std()

    fig2 = plt.figure(1)

    df_chomage[pays].plot(label=pays)
    plt.plot(df_chomage.drop([pays,'Variables'], axis=1).values @ W, label="Contrôle Synthétique")
    plt.vlines(84, 0, 100, linestyle='--', color='red', label='Election de Trump')

    plt.title('Graphique du chomage : {0}'.format(pays))
    plt.xlabel('Années')
    plt.ylabel('Chomage en pourcentage')
    plt.fill_between(df_chomage.index,
        np.array((sc_chomage - 2*error).reshape(100), dtype=float),
        np.array((sc_chomage + 2*error).reshape(100), dtype=float),
        color='0.75')
    plt.legend()
    plt.show()
    #plt.close()

    return(fig1, fig2)

# On vérifie que les fonctions marchent bien.
X1, X0 = prep_donnee('United-States')
W_US, V_US, RMSPE_US = synth(X1, X0)
fig_pib, fig_cho = synth_plot(W_US, 'United-States')


# ------------Partie construction d'un placebo ---------------------------------------------
def in_time_placebo(pays):
    result_time = {}
    date = {t:liste_date([1995,2019])[t:t+13] for t in range(85)}
    for t in date.keys():
        X1, X0 = prep_donnee(pays, date=date[t], placebo=True)
        W_US, V_US, RMSPE_US = synth(X1, X0,pays)
        RMSPE_test=np.linalg.norm((df_pib.loc[date[t],pays].to_numpy(dtype = 'float').reshape(13,1)- (df_pib.drop([pays,'Variables'],axis = 1).loc[date[t]].to_numpy(dtype = 'float')@W).reshape(13,1)))/len(date[t])**(1/2)
        RMSPE_cho_test = np.linalg.norm((df_chomage.loc[date[t],pays].to_numpy(dtype = 'float').reshape(13,1)- (df_chomage.drop([pays,'Variables'],axis = 1).loc[date[t]].to_numpy(dtype = 'float')@W).reshape(13,1)))/(len(date[t])**(1/2))
        RMSPE_cho_train = np.linalg.norm((df_chomage.drop(date[t],axis = 0)[pays].to_numpy(dtype = 'float') - df_chomage.drop([pays,'Variables'],axis = 1).loc[df_chomage.index.difference(date[t])].to_numpy(dtype = 'float') @ W))/((len(df_chomage.index)-len(date[t]))**(1/2))
        result_time[str(date[t][0]) + ' à '+ str(date[t][12])]= [RMSPE_US/82**1/2,RMSPE_test,RMSPE_cho_train,RMSPE_cho_test]
    return result_time

def in_space_placebo():
    result_pays = {}
    W_pays = pd.DataFrame()
    for pays in pays_ocde.keys():
        date = liste_date()
        X1, X0 = prep_donnee(pays)
        W, V, RMSPE_pre = synth(X1, X0,pays)
        W_pays[pays]=W.tolist()
        RMSPE_post = np.linalg.norm((df_pib.loc[date, pays].to_numpy(dtype='float').reshape(12, 1) - (df_pib.drop([pays, 'Variables'], axis=1).loc[date].to_numpy(dtype='float') @ W).reshape(12,1))) / len(date) ** (1 / 2)
        RMSPE_cho_test = np.linalg.norm((df_chomage.loc[date,pays].to_numpy(dtype = 'float').reshape(12,1)- (df_chomage.drop([pays,'Variables'],axis = 1).loc[date].to_numpy(dtype = 'float')@W).reshape(12,1)))/(len(date)**(1/2))
        RMSPE_cho_train = np.linalg.norm((df_chomage.drop(date,axis = 0)[pays].to_numpy(dtype = 'float') - df_chomage.drop([pays,'Variables'],axis = 1).loc[df_chomage.index.difference(date)].to_numpy(dtype = 'float') @ W))/((len(df_chomage.index)-len(date))**(1/2))
        result_pays[pays] = (RMSPE_pre,RMSPE_post,RMSPE_cho_train,RMSPE_cho_test)
    return result_pays,W_pays

def plot_placebo(result,count_fig,relief,numerous = False):
    df_rapport = pd.DataFrame(result,index = ['RMSPE_pre','RMSPE_post','RMSPE_cho_train','RMSPE_cho_test']).T
    df_rapport['Rapport_RMSPE_PIB'] = df_rapport['RMSPE_post']/df_rapport['RMSPE_pre']
    df_rapport.sort_values('Rapport_RMSPE_PIB',inplace=True)
    df_rapport['classement'] = list(t for t in range(len(df_rapport.index)))
    fig = plt.figure(count_fig)
    ax = fig.add_subplot(111)
    if numerous:
        ax.yaxis.set_major_locator(ticker.FixedLocator([df_rapport.loc[relief,'classement']]))
        ax.yaxis.set_minor_locator(ticker.FixedLocator(list(df_rapport['classement'])))
        ax.yaxis.set_ticklabels([relief])
    else :
        ax.yaxis.set_major_locator(ticker.FixedLocator(list(df_rapport['classement'])))
        ax.yaxis.set_ticklabels(df_rapport.index)

    plt.scatter(df_rapport['Rapport_RMSPE_PIB'].drop(relief).to_numpy(dtype='float'),
                df_rapport['classement'].drop(relief).to_numpy(dtype='float'))
    plt.scatter(df_rapport.loc[relief,'Rapport_RMSPE_PIB'],df_rapport.loc[relief,'classement'],marker='+')

    plt.xlabel('Rapport des RMSPE post et pré intervention')

    return fig
'''
result_in_time= in_time_placebo('United-States')
fig1 = plot_placebo(result_in_time,0,'2016-Q1 à 2019-Q1',numerous = True)
plt.savefig('placebo_in_time',bbox_inches='tight')
plt.close()
'''

result_in_space,W_pays = in_space_placebo()
fig2 = plot_placebo(result_in_space,1,'United-States')
plt.savefig('placebo_in_space',bbox_inches='tight')
plt.close()
W_pays.to_csv('W_pays.csv')

def delete_liste(serie):
    for i in range(len(serie)) :
        serie[i]= serie[i][0]
    return(serie)
W_pays.transform(delete_liste)
sc = np.zeros((100,25))
i=0
for pays in df_pib.drop('Variables',axis=1).columns:
    sc[:,i] = (df_pib.drop([pays,'Variables'],axis = 1).to_numpy(dtype='float')@W_pays[pays].to_numpy(dtype='float').reshape(24,1)).reshape(100)
    i+=1

sc = df_pib.drop('Variables',axis = 1).to_numpy(dtype='float') - sc
fig_comp = plt.figure()
ax = fig_comp.add_subplot(111)
for i in range(sc.shape[1]-1):
    plt.plot(sc[:,i],
             color = 'gray',
             alpha=0.7)
plt.plot(sc[:,24],
         color='red',
         label='Etats-Unis')

plt.vlines(84, -1.5, 1.5, linestyle='--', color='red', label='Election de Trump')
plt.xlabel('Années')
plt.ylabel('Ecart entre le contrôle synthétique et la vraie séries temporelles')
plt.legend()
plt.savefig('Ecart au controle synthétique',bbox_inches='tight')

