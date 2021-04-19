
##########   Package    ###########
#install.packages(Synth)
library(datasets)
library(dbplyr)
library(dplyr)
library(stringr)
library(Synth)
library(tidyr)
library(readxl)
library(SCtools)
library(data.table)



##########   Import des données    ###########
tableR <- read.csv("C:/Users/adxva/OneDrive/Bureau/ENSAE 2A - S1/STAT APP/dfR_complete.csv")

# On met les dates en un format numérique
tableR$TIME <- str_replace_all(tableR$TIME, "[:punct:]Q1", ".00" )
tableR$TIME <- str_replace_all(tableR$TIME, "[:punct:]Q2", ".25" )
tableR$TIME <- str_replace_all(tableR$TIME, "[:punct:]Q3", ".50" )
tableR$TIME <- str_replace_all(tableR$TIME, "[:punct:]Q4", ".75" )
tableR <- transform(tableR, TIME = as.numeric(TIME))
tableR$LOCATION <- as.character(tableR$LOCATION)
str(tableR)

#Création de la liste des prédicteurs
list_predictor <- rep(list(list()), 261)

#PIB
for (i in 1:87) {
  list_predictor[[i]] <- append(list_predictor[[i]], list('PIB', tableR$TIME[i+1], 'mean'))
}
#Emplois
for (j in 1:87) {
  list_predictor[[j+87]]  <- append(list_predictor[[j+87]], list('Emplois', tableR$TIME[j+1], 'mean'))
}
#Actifs
for (k in 1:87) {
  list_predictor[[k+174]]  <- append(list_predictor[[k+174]], list('Actifs', tableR$TIME[k+1], 'mean'))
}

list_pred_pib <- rep(list(list()), 87)

#PIB
for (i in 1:87) {
  list_pred_pib[[i]] <- append(list_pred_pib[[i]], list('PIB', tableR$TIME[i+1], 'mean'))
}

list_pred_emp <- rep(list(list()), 87)

#Emplois
for (i in 1:87) {
  list_pred_emp[[i]] <- append(list_pred_emp[[i]], list('Emplois', tableR$TIME[i+1], 'mean'))
}

#Actifs
list_pred_act <- rep(list(list()), 87)


for (i in 1:87) {
  list_pred_act[[i]] <- append(list_pred_act[[i]], list('Actifs', tableR$TIME[i+1], 'mean'))
}


##########   Création des vecteurs du problème d'optimisation    ###########
dataprep.out <- dataprep(
  foo = tableR,
  predictors = c("Chomage", "Conso_share", "Invest_share", 'NExport_share', 'Labor_prod'),
  predictors.op = "mean",
  time.predictors.prior = 2015.50:2016.50,
  special.predictors = list_predictor,
  dependent = "Chomage",
  unit.variable = "ID_country",
  unit.names.variable = "LOCATION",
  time.variable = "TIME",
  treatment.identifier = 25,
  controls.identifier = 1:24,
  time.optimize.ssr = 1995.00:2016.50,
  time.plot = 1995.00:2020.00)




##########   Vecteurs et matrices obtenus    ###########
dataprep.out$X1  #Vecteur des US
dataprep.out$X0  #Matrice du donor pool
dataprep.out$Z1  #Vecteur du taux de chômage US sur la période d'entraînement
dataprep.out$Z0  #Matrice des taux de chômage des unités de contrôle sur la période d'entraînement


##########   Résolution du problème d'optimisation et résultats    ###########

start.time <- Sys.time()
synth.out <- synth(data.prep.obj = dataprep.out, method = "BFGS")
end.time <- Sys.time()
time.taken <- end.time - start.time
time.taken

#Tableaux des matching et poids
synth.tables <- synth.tab(dataprep.res = dataprep.out, synth.res = synth.out)
synth.tables$tab.pred #Tableau des prédictions comparées aux valeurs observées
synth.tables$tab.w    #Tableau des pondérations
synth.tables$tab.v
gaps <- dataprep.out$Y1plot - (dataprep.out$Y0plot %*% synth.out$solution.w)
gaps  #Ecart entre le PIB prédit par le contrôle synthétique et le PIB observé des US

#write.csv(synth.out$solution.w,"C:/Users/adxva/OneDrive/Bureau/ENSAE 2A - S1/STAT APP/Stat-app-Trumpnomics/pond_r_bl.csv")

##########   Graphiques    ###########
path.plot(synth.res = synth.out, dataprep.res = dataprep.out, Ylab = "Chomage", Xlab = "year", Legend = c("USA", "synthetic"), Legend.position = "topright")
abline(v = 2016.75, col="blue", lwd=3, lty=2)


gaps.plot(synth.res = synth.out, dataprep.res = dataprep.out, Ylab = "gap in unemployment rate", Main = NA)
abline(v = 2016.75, col="blue", lwd=3, lty=2)

#Plot du PIB 

#pred_pib <- read.csv("C:/Users/adxva/OneDrive/Bureau/ENSAE 2A - S1/STAT APP/pred_pib.csv")
pred2_pib <- read.csv("C:/Users/adxva/OneDrive/Bureau/ENSAE 2A - S1/STAT APP/pred2_pib.csv")


gaps_pib <- tableR$PIB[1718:1804] - pred2_pib$X0[1:87]
sd_pib <- sd(gaps_pib)

pib_p <- pred2_pib$X0 + sd_pib
pib_m <- pred2_pib$X0 - sd_pib
#sc_pib <- c(synth.tables$tab.pred[6:92,2], pred_pib$X0)

plot(tableR$TIME[2:101], tableR$PIB[1718:1817], ylab = 'PIB (en variation depuis 1995)', xlab = 'Time', ylim = c(0,1.2), col="blue", type = "l", lty = 1, lwd=4)
#lines(tableR$TIME[2:101], sc_pib, col="red",lty=5)
lines(tableR$TIME[1:101], pred2_pib$X0, col="red", type = "l", lty=1, lwd=4)
lines(tableR$TIME[1:101], pib_p, col="black",lty=2)
lines(tableR$TIME[1:101], pib_m, col="black",lty=2)
abline(v = 2016.75, col="green", lwd=3, lty=2)
legend(1995, 1, legend=c("USA", "contrôle synthétique", "élection de Trump"),
       col=c("blue", "red", "green"), lty=1, cex=0.8)

#Plot du chomage
pred_cho <- read.csv("C:/Users/adxva/OneDrive/Bureau/ENSAE 2A - S1/STAT APP/pred_cho.csv")
chom = pred_cho$sc - sd(pred_cho$USA - pred_cho$sc)
chop = pred_cho$sc + sd(pred_cho$USA - pred_cho$sc)
plot(tableR$TIME[1:101], pred_cho$USA, ylab = 'Taux de chômage', xlab = 'Time', ylim = c(0,12), col="blue", type = "l", lty = 1, lwd=4)
lines(tableR$TIME[1:101], chom, col="black",lty=3)
lines(tableR$TIME[1:101], chop, col="black",lty=3)
lines(tableR$TIME[1:101], pred_cho$sc, col="red", type = "l", lty=1, lwd=4)
abline(v = 2016.75, col="green", lwd=3, lty=2)
legend(1995, 12, legend=c("USA", "contrôle synthétique", "élection de Trump"),
       col=c("blue", "red", "green"), lty=1, cex=0.8)

#Plot de l'emploi
pred_emp <- read.csv("C:/Users/adxva/OneDrive/Bureau/ENSAE 2A - S1/STAT APP/pred_emp.csv")
empm <- pred_emp$sc - sd(pred_emp$USA - pred_emp$sc)
empp <- pred_emp$sc + sd(pred_emp$USA - pred_emp$sc)

plot(tableR$TIME[1:101], pred_emp$USA, ylab = 'Emplois', xlab = 'Time', ylim = c(0,0.5), col="red", type = "l", lty = 1, lwd=4)
lines(tableR$TIME[1:101], pred_emp$sc, col="blue", type = "l", lty=1, lwd=4)
lines(tableR$TIME[1:101], empm, col="black",lty=3)
lines(tableR$TIME[1:101], empp, col="black",lty=3)
abline(v = 2016.75, col="green", lwd=3, lty=2)
legend(1995, 0.5, legend=c("USA", "contrôle synthétique", "élection de Trump"),
       col=c("red", "blue", "green"), lty=1, cex=0.8)

#Plot des actifs
pred_actifs <- read.csv("C:/Users/adxva/OneDrive/Bureau/ENSAE 2A - S1/STAT APP/pred_actifs.csv")
actm <- pred_actifs$sc - sd(pred_actifs$USA - pred_actifs$sc)
actp <- pred_actifs$sc + sd(pred_actifs$USA - pred_actifs$sc)

plot(tableR$TIME[1:101], pred_actifs$USA, ylab = 'Actifs', xlab = 'Time', ylim = c(0,0.5), col="red", type = "l", lty = 1, lwd=4)
lines(tableR$TIME[1:101], pred_actifs$sc, col="blue", type = "l", lty=1, lwd=4)
lines(tableR$TIME[1:101], actm, col="black",lty=3)
lines(tableR$TIME[1:101], actp, col="black",lty=3)
abline(v = 2016.75, col="green", lwd=3, lty=2)
legend(1995, 0.5, legend=c("USA", "contrôle synthétique", "élection de Trump"),
       col=c("red", "blue", "green"), lty=1, cex=0.8)

# Robustesse et placebos

tdf <- generate.placebos(dataprep.out,synth.out, Sigf.ipop = 5, strategy = "multiprocess")



mspe.plot(
  tdf,
  discard.extreme = FALSE,
  mspe.limit = 20,
  plot.hist = FALSE,
  title = "Ratio MSPE Chomage",
  xlab = "Post/Pre MSPE ratio",
  ylab = NULL
)
ratio <- mspe.test(tdf)
ratio$p.val
ratio$test

plot_placebos(
  tdf = tdf,
  discard.extreme = FALSE,
  mspe.limit = 20,
  xlab = NULL,
  ylab = NULL,
  title = "Placebo chomage",
  alpha.placebos = 1,
)

placebo <- tdf$df


# Leave one out
country <- c(12, 13, 14, 16, 22)
y0plot1 <- dataprep.out$Y0plot %*% synth.out$solution.w
d <- as.data.frame(y0plot1)

for (i in country) {
  dp.out <- dataprep(
    foo = tableR,
    predictors = c("Chomage", "Conso_share", "Invest_share", 'Export_share', 'Labor_prod'),
    predictors.op = "mean",
    time.predictors.prior = 2015.50:2016.50,
    special.predictors = list_predictor,
    dependent = "Chomage",
    unit.variable = "ID_country",
    unit.names.variable = "LOCATION",
    time.variable = "TIME",
    treatment.identifier = 25,
    controls.identifier = c(1:(i-1),(i+1):24),
    time.optimize.ssr = 1995.00:2016.50,
    time.plot = 1995.00:2020.00)
  s.out <- synth(data.prep.obj = dp.out, method = "BFGS")
  y0plot <- dp.out$Y0plot %*% s.out$solution.w
  d[ , ncol(d) + 1] <- y0plot                  # Append new column
  colnames(d)[ncol(d)] <- paste0("y0plot", i)  # Rename column name
  #d_weight[ , ncol(d_weight) + 1] <- s.out$solution.w        # Append new column
  #colnames(d_weight)[ncol(d_weight)] <- paste0("Weight", i)  # Rename column name
}



plot(dataprep.out$tag$time.plot, dataprep.out$Y1plot, col = 'red', type = 'l',lwd=3, lty=1, xlab = 'Time', ylab = 'Taux de chomage')
lines(dataprep.out$tag$time.plot, d$w.weight, col = 'blue', type = 'l',lwd=3, lty=2)
lines(dataprep.out$tag$time.plot, d$y0plot12, col = 'grey', type = 'l',lwd=2, lty=3)
lines(dataprep.out$tag$time.plot, d$y0plot13, col = 'grey', type = 'l',lwd=2, lty=3)
lines(dataprep.out$tag$time.plot, d$y0plot14, col = 'grey', type = 'l',lwd=2, lty=3)
lines(dataprep.out$tag$time.plot, d$y0plot16, col = 'grey', type = 'l',lwd=2, lty=3)
lines(dataprep.out$tag$time.plot, d$y0plot22, col = 'grey', type = 'l',lwd=2, lty=3)
abline(v = 2016.75, col="black", lwd=3, lty=2)
legend(1995, 10, legend=c("USA", "contrôle synthétique", "élection de Trump", "leave-one-out"),
       col=c("red", "blue", "black", "grey"), lty=c(1,2,3,3,3,3))



################################################################################

#Création de la liste des prédicteurs
list_predictor_pib <- rep(list(list()), 261)

#Chomage
for (i in 1:87) {
  list_predictor_pib[[i]] <- append(list_predictor_pib[[i]], list('Chomage', tableR$TIME[i+1], 'mean'))
}
#Emplois
for (j in 1:87) {
  list_predictor_pib[[j+87]]  <- append(list_predictor_pib[[j+87]], list('Emplois', tableR$TIME[j+1], 'mean'))
}
#Actifs
for (k in 1:87) {
  list_predictor_pib[[k+174]]  <- append(list_predictor_pib[[k+174]], list('Actifs', tableR$TIME[k+1], 'mean'))
}




##########   Création des vecteurs du problème d'optimisation    ###########
dataprep_pib.out <- dataprep(
  foo = tableR,
  predictors = c("PIB", "Conso_share", "Invest_share", 'Export_share', 'Labor_prod'),
  predictors.op = "mean",
  time.predictors.prior = 2015.50:2016.50,
  special.predictors = list_predictor_pib,
  dependent = "PIB",
  unit.variable = "ID_country",
  unit.names.variable = "LOCATION",
  time.variable = "TIME",
  treatment.identifier = 25,
  controls.identifier = 1:24,
  time.optimize.ssr = 1995.00:2016.50,
  time.plot = 1995.00:2020.00)


##########   Résolution du problème d'optimisation et résultats    ###########

start.time <- Sys.time()
synth_pib.out <- synth(data.prep.obj = dataprep_pib.out, method = "BFGS")
end.time <- Sys.time()
time.taken <- end.time - start.time
time.taken

#Tableaux des matching et poids
synth_pib.tables <- synth.tab(dataprep.res = dataprep_pib.out, synth.res = synth_pib.out)
synth_pib.tables$tab.pred #Tableau des prédictions comparées aux valeurs observées
synth_pib.tables$tab.w    #Tableau des pondérations
synth_pib.tables$tab.v
gaps_pib <- dataprep_pib.out$Y1plot - (dataprep_pib.out$Y0plot %*% synth_pib.out$solution.w)
gaps_pib  #Ecart entre le PIB prédit par le contrôle synthétique et le PIB observé des US

#write.csv(synth.out$solution.w,"C:/Users/adxva/OneDrive/Bureau/ENSAE 2A - S1/STAT APP/ponderation.csv")

##########   Graphiques    ###########
path.plot(synth.res = synth_pib.out, dataprep.res = dataprep_pib.out, Ylab = "PIB", Xlab = "year", Legend = c("USA", "synthetic"), Legend.position = "topright")
abline(v = 2016.75, col="blue", lwd=3, lty=2)


gaps.plot(synth.res = synth_pib.out, dataprep.res = dataprep_pib.out, Ylab = "gap in GDP", Main = NA)
abline(v = 2016.75, col="blue", lwd=3, lty=2)


# Robustesse et placebos
start.time <- Sys.time()
tdf <- generate.placebos(dataprep_pib.out,synth_pib.out, Sigf.ipop = 5, strategy = "multiprocess")
end.time <- Sys.time()
time.taken <- end.time - start.time
time.taken



mspe.plot(
  tdf_pib,
  discard.extreme = FALSE,
  mspe.limit = 20,
  plot.hist = FALSE,
  title = "MSPE Ratio PIB",
  xlab = "Post/Pre MSPE ratio",
  ylab = NULL
)
ratio_pib <- mspe.test(tdf)
ratio_pib$p.val
ratio_pib$test

plot_placebos(
  tdf = tdf_pib,
  discard.extreme = FALSE,
  mspe.limit = 20,
  xlab = NULL,
  ylab = NULL,
  title = "Placebo PIB",
  alpha.placebos = 1,
)


# Leave one out
country <- c(12, 13, 14, 16, 22)

d <- as.data.frame(y0plot1)
for (i in country) {
  dp.out <- dataprep(
    foo = tableR,
    predictors = c("Chomage", "Conso_share", "Invest_share", 'Export_share', 'Labor_prod'),
    predictors.op = "mean",
    time.predictors.prior = 2015.50:2016.50,
    special.predictors = list_predictor,
    dependent = "Chomage",
    unit.variable = "ID_country",
    unit.names.variable = "LOCATION",
    time.variable = "TIME",
    treatment.identifier = 25,
    controls.identifier = c(1:(i-1),(i+1):24),
    time.optimize.ssr = 1995.00:2016.50,
    time.plot = 1995.00:2020.00)
  s.out <- synth(data.prep.obj = dp.out, method = "BFGS")
  y0plot <- dp.out$Y0plot %*% s.out$solution.w
  d[ , ncol(d) + 1] <- y0plot                  # Append new column
  colnames(d)[ncol(d)] <- paste0("y0plot", i)  # Rename column name
  d[ , ncol(d) + 2] <- s.out$solution.w        # Append new column
  colnames(d)[ncol(d)] <- paste0("Weight", i)  # Rename column name
}



plot(dataprep.out$tag$time.plot, dataprep.out$Y1plot, col = 'red', type = 'l',lwd=3, lty=1, xlab = 'Time', ylab = 'Taux de chomage')
lines(dataprep.out$tag$time.plot, d$w.weight, col = 'blue', type = 'l',lwd=3, lty=2)
lines(dataprep.out$tag$time.plot, d$y0plot12, col = 'grey', type = 'l',lwd=2, lty=3)
lines(dataprep.out$tag$time.plot, d$y0plot13, col = 'grey', type = 'l',lwd=2, lty=3)
lines(dataprep.out$tag$time.plot, d$y0plot14, col = 'grey', type = 'l',lwd=2, lty=3)
lines(dataprep.out$tag$time.plot, d$y0plot16, col = 'grey', type = 'l',lwd=2, lty=3)
lines(dataprep.out$tag$time.plot, d$y0plot22, col = 'grey', type = 'l',lwd=2, lty=3)
abline(v = 2016.75, col="black", lwd=3, lty=2)
legend(1995, 10, legend=c("USA", "contrôle synthétique", "élection de Trump", "leave-one-out"),
       col=c("red", "blue", "black", "grey"), lty=c(1,2,3,3,3,3))


###############################################################################

######## TIME PLACEBO

list_pred_2011 <- rep(list(list()), 189)

#PIB
for (i in 1:63) {
  list_pred_2011[[i]] <- append(list_pred_2011[[i]], list('Chomage', tableR$TIME[i+1], 'mean'))
}
#Emplois
for (j in 1:63) {
  list_pred_2011[[j+63]]  <- append(list_pred_2011[[j+63]], list('Emplois', tableR$TIME[j+1], 'mean'))
}
#Actifs
for (k in 1:63) {
  list_pred_2011[[k+126]]  <- append(list_pred_2011[[k+126]], list('Actifs', tableR$TIME[k+1], 'mean'))
}


##########   Création des vecteurs du problème d'optimisation    ###########
dp2011.out <- dataprep(
  foo = tableR,
  predictors = c("PIB", "Conso_share", "Invest_share", 'Export_share', 'Labor_prod'),
  predictors.op = "mean",
  time.predictors.prior = 2009.50:2010.75,
  special.predictors = list_pred_2011,
  dependent = "PIB",
  unit.variable = "ID_country",
  unit.names.variable = "LOCATION",
  time.variable = "TIME",
  treatment.identifier = 25,
  controls.identifier = 1:24,
  time.optimize.ssr = 1995.00:2010.75,
  time.plot = 1995.00:2020.00)



##########   Résolution du problème d'optimisation et résultats    ###########

start.time <- Sys.time()
synth2011.out <- synth(data.prep.obj = dp2011.out, method = "BFGS")
end.time <- Sys.time()
time.taken <- end.time - start.time
time.taken

#Tableaux des matching et poids
synth2011.tables <- synth.tab(dataprep.res = dp2011.out, synth.res = synth2011.out)
synth2011.tables$tab.pred #Tableau des prédictions comparées aux valeurs observées
synth2011.tables$tab.w    #Tableau des pondérations
synth2011.tables$tab.v
gaps2011 <- dp2011.out$Y1plot - (dp2011.out$Y0plot %*% synth2011.out$solution.w)
gaps2011  #Ecart entre le PIB prédit par le contrôle synthétique et le PIB observé des US

#write.csv(synth.out$solution.w,"C:/Users/adxva/OneDrive/Bureau/ENSAE 2A - S1/STAT APP/ponderation.csv")

##########   Graphiques    ###########
path.plot(synth.res = synth2011.out, dataprep.res = dp2011.out, Ylab = "PIB", Xlab = "year", Legend = c("USA", "synthetic"), Legend.position = "topright")
abline(v = 2011, col="blue", lwd=3, lty=2)
#lines(tableR$TIME[1:101], pred_cho$sc, col="red", type = "l", lty=1, lwd=4)


gaps.plot(synth.res = synth2011.out, dataprep.res = dp2011.out, Ylab = "gap in unemployment rate", Main = NA)
abline(v = 2016.75, col="blue", lwd=3, lty=2)


