class Sensor:
    def __init__(self, id, name, latency, priority):
        self.id = id
        self.name = name
        self.latency = latency
        self.priority = priority

    def sendData(self, lb, priority, latency, data, fogs):
        # print('sending...')
        lb.allocatedTask(priority, latency, data, fogs)
        # Gateway.doTask(data, latency, data)

    def getLatency(self):
        return self.latency
    def getPriority(self):
        return self.priority
    def getId(self):
        return self.id
