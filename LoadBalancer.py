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
    def __init__(self, id=1):
        self.id = id
    def allocatedTask(self, priority, latency, data, fogs):
        '''
        if(len(fogs) == 1):
            fogs[0].doTask(data, latency)
        else:
        '''
        self.getBestFogDevice(priority, fogs).doTask(data,latency)

    def getBestFogDevice(self, priority, fogs):
        if (priority == 1):
            for f in fogs:
                self.evaluations[f.id] = f.getEvaluation()
                # f.showState()
        best_fog = max(self.evaluations, key=lambda k: self.evaluations[k])
        with self._lock:
            print('\nbest_fog: ', best_fog, 'evaluation: ', self.evaluations[best_fog])
        # print(self.evaluations)
        # return fogs[best_fog]
        return fogs[random.randint(0,9)]