setwd("~/workspace/IC/matplot/result")

orderSimulation <- read.csv("/Users/fernando/workspace/IC/SmartClassFogLB/v2/testes.csv",
                            col.names = c("index", "nodoSize", "levelTask", "requestsNumber"),
                            header = FALSE)

orderSimulation[,"meanTime"] <- sapply(orderSimulation[1:3,"index"], calcMean)
show(orderSimulation)

# install.packages("rjson")
# library("rjson")
# 
# resultData <- rjson::fromJSON(file = "teste 1")
# resultDataFrame = as.data.frame(resultData)
# show(colnames(resultDataFrame))

# install.packages("jsonlite")
library(jsonlite)
resultData <- jsonlite::fromJSON("teste 1", flatten=TRUE)
resultDataFrame = as.data.frame(resultData)
# show(resultDataFrame)

# for (ln in 1:nrow(resultDataFrame)) {
#   row <- resultDataFrame[ln,]
#   resultDataFrame[ln, "interval"] <- row["times.processEnd"] - row["times.bornTime"]
# }

calcMean <- function(index) {
  resultData <- jsonlite::fromJSON(paste("teste", index), flatten=TRUE)
  resultDataFrame = as.data.frame(resultData)
  resultDataFrame[, "interval"] <- resultDataFrame[,"times.processEnd"] - resultDataFrame[,"times.bornTime",]
  meanForConfig <- mean(resultDataFrame[,"interval"])
}

meanForConfig <- sapply(orderSimulation$index, calcMean)

show(meanForConfig)






amostra <- results[results["nodoSize"] == nodoSize, ]
df <- data.frame(matrix(ncol = length(requests), nrow = 6))
colnames(df) <- requests
rownames(df) <- amostra[["index"]]
df[amostra[index],amostra["requestsNumber"]] <- amostra["meanTimeNormalPriority"]
split(amostra, requests)
consegui <- by(amostra, amostra["requestsNumber"], function(x) x)
df[,requests] <- consegui[31,"meanTimeNormalPriority",requests]
dim(consegui)

