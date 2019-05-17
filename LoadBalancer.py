import threading as th
import random

class LoadBalancer:
    fogDevices = dict()
    encaminhados = dict()
    droped = dict()
    tempos = dict()
    loads = dict()
    cpu = dict()
    _lock = th.Lock()

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
        print(self.cpu)
        with self._lock:
            if (priority == 1):
                for f in self.fogDevices:
                    if f.getLoadAverage() > 0:
                        cpuEval = ((f.cpuCoreCount*f.frequency)/f.getLoadAverage()) + f.ram + f.storageAmount
                    else:
                        cpuEval = (f.cpuCoreCount*f.frequency)*100 + f.ram + f.storageAmount
                    self.cpu[f.id] = cpuEval
                    print('\nid: ',f.id, '\ncpuCount:', f.cpuCoreCount,
                            '\nram: ',f.ram, '\nstorage: ', f.storageAmount, '\nrede: ',
                            f.downloadbandwith, '\nLatency', f.latency, '\nfrequencia: ',
                            f.frequency, '\nevaluation: ', cpuEval)

                #TODO!!
                #fazer os gets and sets

                dev = random.randint(0,100)
                fogs = len(self.fogDevices)
                if (self.fogDevices[random.randint(0,fogs-1)].getLoadAverage() >= (self.fogDevices[random.randint(0,fogs-1)].getCpuCount()*100)*0.8):
                    pass
                    # print('fog eleita: ' + str(self.fogDevices[random.randint(0,fogs-1)].id))
                return self.fogDevices[random.randint(0,fogs-1)]
            else:
                # fogDevices.sort(o1,o2) #ordena e pega o menor loadAvg
                return fogDevices[random.randint(0,fogs-1)]
