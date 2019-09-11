# install.packages("jsonlite")
# install.packages("tictoc")
library(jsonlite)
library(tictoc)

setwd("~/workspace/IC/matplot/result")

tic("calc mean")

calcMeanByFile <- function(index) {
  resultData <- jsonlite::fromJSON(paste("teste", index), flatten=TRUE)
  resultDataFrame = as.data.frame(resultData)
  
  data.frame(row.names = c(index))
  resultDataFrame[, "interval"] <- resultDataFrame[,"times.processEnd"] - resultDataFrame[,"times.bornTime",]
  result <- data.frame(row.names = c(index))
  result["index"] <- index
  result["meanTimeNormalPriority"] <- mean(resultDataFrame[resultDataFrame["priority"] == 0, "interval"])
  result["standardDeviationNormalPriority"] <- sd(resultDataFrame[resultDataFrame["priority"] == 0, "interval"])
  result["meanTimeHightPriority"] <- -1 * mean(resultDataFrame[resultDataFrame["priority"] == 1, "interval"])
  result["standardDeviationHightPriority"] <- -1 * sd(resultDataFrame[resultDataFrame["priority"] == 1, "interval"])
  
  return(result)
}

orderSimulation <- read.csv("/Users/fernando/workspace/IC/SmartClassFogLB/v2/testes.csv",
                            col.names = c("index", "nodoSize", "levelTask", "requestsNumber"),
                            header = FALSE)

res <- sapply(orderSimulation$index, calcMeanByFile)

orderSimulation <- merge(orderSimulation, t(res), by = "index")

toc()

# show(as.matrix.data.frame(orderSimulation))

write.csv(as.matrix.data.frame(orderSimulation),
          file = "/Users/fernando/workspace/IC/SmartClassFogLB/v2/testesEResultadosParaPlot.csv",
          row.names = FALSE)
