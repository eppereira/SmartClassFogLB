setwd("~/workspace/IC/SmartClassFogLB/plot/result")

results <- read.csv("/Users/fernando/workspace/IC/SmartClassFogLB/v2/testesEResultadosParaPlot.csv",
                    header = TRUE)

for (nodoSize in unique(results$nodoSize)) {
  # Preparando a matriz de dados para o gráfico
  requests <- unique(results[results["nodoSize"] == nodoSize, "requestsNumber"])
  colsLength <- length(requests)
  results4plotNormalPriority <- matrix(nrow = 0, ncol = colsLength)
  results4plotHightPriority <- matrix(nrow = 0, ncol = colsLength)
  sd4plotNormalPriority <- matrix(nrow = 0, ncol = colsLength)
  sd4plotHightPriority <- matrix(nrow = 0, ncol = colsLength)
  
  for (nr in 1:length(requests)) {
      for (i in results[results$nodoSize == nodoSize & results$requestsNumber == requests[nr], "index"]) {
        newLine <- integer(colsLength)
        newLine[nr] <- results[i, "meanTimeNormalPriority"]
        results4plotNormalPriority <- rbind(results4plotNormalPriority, newLine)
        
        # newLine <- vector("list", length = colsLength)
        # newLine[nr] <- list(results[i, "meanTimeNormalPriority"] - results[i, "standardDeviationNormalPriority"],
        #                     results[i, "meanTimeNormalPriority"] + results[i, "standardDeviationNormalPriority"])
        # sd4plotNormalPriority <- rbind(results4plotNormalPriority, newLine)
        
        newLine <- integer(colsLength)
        newLine[nr] <- results[i, "meanTimeHightPriority"]
        results4plotHightPriority <- rbind(results4plotHightPriority, newLine)
      }
  }
  
  
  # Configurando o gráfico
  colors <- c("green","orange","brown")
  # colors <- data.frame(c("green","orange","brown"))
  palette(rainbow(6))
  colorRampPalette(colors)
  
  requests <- sapply(requests, toString)
  sizeTasks <- c("Tarefa Leve", "Tarefa Média", "Tarefa Pesada")
  png(file = paste(nodoSize, ".png", sep = ""))
  limTopMax <- max(results[results["nodoSize"] == nodoSize, "meanTimeNormalPriority"] + results[results["nodoSize"] == nodoSize, "standardDeviationNormalPriority"])
  limTopFirstCol <- 1.8 * results[results["nodoSize"] == nodoSize, "meanTimeNormalPriority"][1] + results[results["nodoSize"] == nodoSize, "standardDeviationNormalPriority"][1]
  limTop <- ifelse(limTopFirstCol > limTopMax, limTopFirstCol, limTopMax)
  limTopYNormalPriority <- 1.8 * limTop
  limDownYNormalPriority <- 1.1 * min(results[results["nodoSize"] == nodoSize, "meanTimeHightPriority"] + results[results["nodoSize"] == nodoSize, "standardDeviationHightPriority"])
  yLimits <-c(limDownYNormalPriority, limTopYNormalPriority)
  
  barChart <- barplot(results4plotNormalPriority,
                      names.arg = requests,
                      xlab = "Número de Requisições",
                      ylab = "Tempo log(ms)",
                      beside = FALSE,
                      col = colors, density = 30, ylim = yLimits, border = TRUE, axis.lty = 1)
  barChart <- barplot(results4plotHightPriority,
                      beside = FALSE,
                      col = colors, density = 70, add = TRUE, axes = TRUE, border = TRUE, axis.lty = 1)
  arrows(barChart, results[results["nodoSize"] == nodoSize, "meanTimeNormalPriority"] - results[results["nodoSize"] == nodoSize, "standardDeviationNormalPriority"],
         barChart, results[results["nodoSize"] == nodoSize, "meanTimeNormalPriority"] + results[results["nodoSize"] == nodoSize, "standardDeviationNormalPriority"],
         angle=90, code=3)
  arrows(barChart, results[results["nodoSize"] == nodoSize, "meanTimeHightPriority"] - results[results["nodoSize"] == nodoSize, "standardDeviationHightPriority"],
         barChart, results[results["nodoSize"] == nodoSize, "meanTimeHightPriority"] + results[results["nodoSize"] == nodoSize, "standardDeviationHightPriority"],
         angle=90, code=3)
  
  legend("topleft", sizeTasks, cex = 1, fill = colors)
  
  # Salvar imagem do gráfico
  dev.off()
}