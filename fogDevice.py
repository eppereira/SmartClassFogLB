import time
from LoadBalancer import *
import threading as th
loadAverage = dict()
class FogDeviceLB:
    _lock = th.Lock()
    def __init__(self, id, name, cpuCoreCount, ram, storageAmount,\
                        uploadbandwith, downloadbandwith, latency, freq):
        self.id = id
        self.name = name
        self.cpuCoreCount = cpuCoreCount
        self.ram = ram
        self.storageAmount = storageAmount
        self.uploadbandwith = uploadbandwith
        self.downloadbandwith = downloadbandwith
        self.latency = latency
        self.aguardar = 0
        self.dropados = 0
        self.maxLoadAverage = 100*self.cpuCoreCount # 100% por core
        self.limiteAceitavelLoadAvg = self.maxLoadAverage*0.8
        self.loadAverage = 0
        self.frequency = freq #definir no construtor
        self.disk = 8000
        if (self.id not in loadAverage):
            loadAverage[self.id] = 0


    def doTask(self, data, latency):
        self.startTime = time.time() * 1000.0 # retorna em segundos, converte pra milisegundos
        if (self.id in LoadBalancer.encaminhados):
            LoadBalancer.encaminhados[self.id] += 1
        else:
            LoadBalancer.encaminhados[self.id] = 1

        dropou = False
        # print('load: ', loadAverage)
        if(loadAverage[self.id] >= self.maxLoadAverage):
            # print('fog id: ' + str(self.id) + ' sobrecarregada. load: ', loadAverage[self.id])
            if (self.id in LoadBalancer.droped):
                LoadBalancer.droped[self.id] += 1
            else:
                LoadBalancer.droped[self.id] = 1
            dropou = True
            while(loadAverage[self.id] >= self.maxLoadAverage):
                time.sleep(10/1000.)

        if (dropou == False):
            # print('+5', self.id)
            loadAverage[self.id] += 5
            if(loadAverage[self.id] >= self.limiteAceitavelLoadAvg):
                #fog sobrecarregada e penalizada com tempo
                self.aguardar = 10/1000.
                time.sleep(self.aguardar)
            time.sleep(self.latency)

            if(loadAverage[self.id] != 0):
                loadAverage[self.id] -= 5
                # print('-5', self.id)


        self.stopTime = time.time() * 1000.0
        self.elapsedTime = self.startTime - self.stopTime
        try:
            with self._lock: #ver se funciona
                if (self.id in LoadBalancer.tempos):
                    LoadBalancer.tempos[self.id] += 1
                else:
                    LoadBalancer.tempos[self.id] = 1

                if (self.id in LoadBalancer.loads):
                    LoadBalancer.loads[self.id] += 1
                else:
                    LoadBalancer.loads[self.id] = 1
        except:
            print('erro')

    def getLoadAverage(self):
        return loadAverage[self.id]
    def getCpuCount(self):
        return self.cpuCoreCount
#TODO gets and sets
