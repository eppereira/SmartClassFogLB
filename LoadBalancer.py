import threading as th
import random
from fogDevice import *

class LoadBalancer:
    fogDevices = dict()
    encaminhados = dict()
    droped = dict()
    tempos = dict()
    loads = dict()
    cpu = dict()
    _lock = th.Lock()
    evaluations = dict()
    def __init__(self, fogs, id):
        self.fogDevices = fogs
        self.id = id
    def allocatedTask(self, idSensor, priority, latency, data):
        if(len(self.fogDevices) == 1):
            self.fogDevices[0].doTask(data, latency)
        else:
            self.getBestFogDevice(priority).doTask(data,latency)

    def getBestFogDevice(self, priority):
        if (priority == 1):
            for f in self.fogDevices:
                self.evaluations[f.id] = f.getEvaluation()
                f.showState()
        best_fog = max(self.evaluations, key=lambda k: self.evaluations[k])
        # print('\nbest_fog: ', best_fog)
        return self.fogDevices[best_fog]
