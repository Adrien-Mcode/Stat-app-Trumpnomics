tableR$Conso <- with(tableR, Conso/PIB)
tableR$Formation <- with(tableR, Formation/PIB)
tableR$Exports <- with(tableR, Exports/PIB)

tableR$Dates <- str_replace_all(tableR$Dates, "[:punct:]Q", "." )
tableR <- transform(tableR, Dates = as.numeric(Dates))
tableR$Pays <- as.character(tableR$Pays)
str(tableR)

dataprep.out <- dataprep(
  foo = tableR,
  predictors = c("PIB", "Emplois","Actifs"),
  predictors.op = "mean",
  time.predictors.prior = 1996.1:2016.4,
  special.predictors = list(
    list("Chomage", 2015.3:2016.3 , "mean"),
    list("Conso", 2015.3:2016.3, "mean"),
    list("Formation", 2015.3:2016.3, "mean"),
    list("Exports", 2015.3:2016.3, "mean")
    ),
  dependent = "PIB",
  unit.variable = "numero",
  unit.names.variable = "Pays",
  time.variable = "Dates",
  treatment.identifier = 25,
  controls.identifier = 1:24,
  time.optimize.ssr = 1996.1:2016.4,
  time.plot = 1996.1:2019.4)

synth.out <- synth(data.prep.obj = dataprep.out, method = "BFGS")

path.plot(synth.res = synth.out, dataprep.res = dataprep.out, Ylab = "real GDP", Xlab = "year", Legend = c("USA", "synthetic"), Legend.position = "bottomright")
