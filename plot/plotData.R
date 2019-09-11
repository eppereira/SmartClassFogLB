setwd("~/workspace/IC/matplot/result")

results <- read.csv("/Users/fernando/workspace/IC/SmartClassFogLB/v2/testesEResultadosParaPlot.csv",
                    header = TRUE)

# Preparando a matriz de dados para o gráfico
nodoSize <- "mixed"
requests <- unique(results[results["nodoSize"] == nodoSize, "requestsNumber"])
colsLength <- length(requests)
results4plot <- matrix(nrow = 0, ncol = colsLength)
# results4plot <- rbind(results4plot, results[results["nodoSize"] == nodoSize, "meanTimeNormalPriority"])
# results4plot <- rbind(results4plot, results[results["nodoSize"] == nodoSize, "meanTimeHightPriority"])

for (nr in 1:length(requests)) {
  for (i in results[results$nodoSize == nodoSize & results$requestsNumber == requests[nr], "index"]) {
    newLine <- integer(colsLength)
    newLine[nr] <- results[i, "meanTimeHightPriority"]
    results4plot <- rbind(results4plot, newLine)
  }
}


# Configurando o gráfico
colors <- c("green","orange","brown")
requests <- sapply(requests, toString)
sizeTasks <- c("Tarefa Leve", "Tarefa Média", "Tarefa Pesada")
png(file = paste(nodoSize, ".png", sep = ""))
limTopMax <- max(results[results["nodoSize"] == nodoSize, "meanTimeNormalPriority"] + results[1, "standardDeviationNormalPriority"])
limTopFirstCol <- 1.8 * results[results["nodoSize"] == nodoSize, "meanTimeNormalPriority"][1] + results[1, "standardDeviationNormalPriority"][1]
limTop <- ifelse(limTopFirstCol > limTopMax, limTopFirstCol, limTopMax)
limTopYNormalPriority <- 1.8 * limTop
limDownYNormalPriority <- 1.1 * min(results[results["nodoSize"] == nodoSize, "meanTimeHightPriority"] + results[results["nodoSize"] == nodoSize, "standardDeviationHightPriority"])
yLimits <-c(limDownYNormalPriority, limTopYNormalPriority)

barChart <- barplot(results4plot,
                    names.arg = requests,
                    xlab = "Número de Requisições",
                    ylab = "Tempo log(ms)",
                    beside = FALSE,
                    col = colors, density = 30, ylim = yLimits, border = TRUE, axis.lty = 1)
barChart <- barplot(results4plot[2, results["nodoSize"] == nodoSize],
                    beside = FALSE,
                    col = colors, density = 70, add = TRUE, axes = TRUE, border = TRUE, axis.lty = 1)
arrows(barChart, results[results["nodoSize"] == nodoSize, "meanTimeNormalPriority"] - results[results["nodoSize"] == nodoSize, "standardDeviationNormalPriority"],
       barChart, results[results["nodoSize"] == nodoSize, "meanTimeNormalPriority"] + results[results["nodoSize"] == nodoSize, "standardDeviationNormalPriority"],
       angle=90, code=3)
arrows(barChart, results[results["nodoSize"] == nodoSize, "meanTimeHightPriority"] - results[results["nodoSize"] == nodoSize, "standardDeviationHightPriority"],
       barChart, results[results["nodoSize"] == nodoSize, "meanTimeHightPriority"] + results[results["nodoSize"] == nodoSize, "standardDeviationHightPriority"],
       angle=90, code=3)

# barplot(results4plot[1,results["nodoSize"] == nodoSize], log = "y")

legend("topleft", sizeTasks, cex = 1, fill = colors)

# Salvar imagem do gráfico
dev.off()

