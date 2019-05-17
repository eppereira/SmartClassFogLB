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
        # self.fogDevices = list()
        self.fogDevices = fogs
        self.id = id
    def allocatedTask(self, idSensor, priority, latency, data):
        # try:
        if(len(self.fogDevices) == 1):
            self.fogDevices[0].doTask(data, latency)
        else:
            self.getBestFogDevice(priority).doTask(data,latency)
        #except:
        #    print("erro aqui ")

    def getBestFogDevice(self, priority):
        # cpu = dict()
        net = list()
        # print(self.cpu)
        # with self._lock:
        if (priority == 1):
            #evaluation:
            '''
            A = CPU
            B = FREQ
            C = LOAD
            D = RAM
            E = RAM DISP
            F = DISCO
            G = DISCO DISP
            IF(((C5*100)/A5)>=90;0;
            IF(E5<=(D5-(D5*0,9));0;
            IF(G5<=(F5-(F5*0,9));0;
            (A5*B5)/((C5*100)/A5))+(E5/100)+(G5/1000)))
            '''
            for f in self.fogDevices:
                self.evaluations[f.id] = f.getEvaluation()
                f.showState()
        # best_fog = (max(self.evaluations))
        best_fog = max(self.evaluations, key=lambda k: self.evaluations[k])
        # print('\nbest_fog: ', best_fog)
        return self.fogDevices[best_fog]

'''                # cpuEval = (f.cpuCoreCount*f.frequency)*100 + f.ram + f.storageAmount
                # self.cpu[f.id] = cpuEval
            #TODO!!
            #fazer os gets and sets

            dev = random.randint(0,100)
            fogs = len(self.fogDevices)
            if (self.fogDevices[best_fog].getLoadAverage() >= (self.fogDevices[best_fog].getCpuCount()*100)*0.8):
                pass
                print('fog eleita: ' + str(self.fogDevices[random.randint(0,fogs-1)].id))

        return self.fogDevices[best_fog]
        else:
            # fogDevices.sort(o1,o2) #ordena e pega o menor loadAvg
'''
