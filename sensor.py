class Sensor:
    def __init__(self, id, name, gatewayId, latency, priority):
        self.id = id
        self.name = name
        self.gatewayId = gatewayId
        self.latency = latency
        self.priority = priority

    def sendData(self, lb, gatewayId, priority, latency, data):
        # print('sending...')
        lb.allocatedTask(self.id, priority, latency, data)
        # Gateway.doTask(data, latency, data)

    def getLatency(self):
        return self.latency
    def getPriority(self):
        return self.priority
    def getId(self):
        return self.id
