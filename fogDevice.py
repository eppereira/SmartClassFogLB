import time
from LoadBalancer import *
import threading as th

loadAverage = dict()
ramDisp = dict()
discoDisp = dict()
redeUtilizada = dict()
evaluations = dict()

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
        self.maxLoadAverage = 100 * self.cpuCoreCount # 100% por core
        self.limiteAceitavelLoadAvg = self.maxLoadAverage*0.9
        self.loadAverage = 0
        self.frequency = freq # faz sentido usar?
        if (self.id not in loadAverage):
            loadAverage[self.id] = 0
            ramDisp[self.id] = self.ram
            discoDisp[self.id] = self.storageAmount
            redeUtilizada[self.id] = 0


    def doTask(self, data, latency):
        self.startTime = time.time() * 1000.0 # retorna em segundos, converte pra milisegundos
        if (self.id in LoadBalancer.encaminhados):
            LoadBalancer.encaminhados[self.id] += 1
        else:
            LoadBalancer.encaminhados[self.id] = 1

        dropou = False
        # print('load: ', loadAverage)
        if((loadAverage[self.id] >= self.maxLoadAverage)):
            ''' or
            (ramDisp[self.id] < self.ram) or
            (discoDisp[self.id] < self.storageAmount) or
            redeUtilizada[self.id] > self.downloadbandwith):
            '''
            # print('fog id: ' + str(self.id) + ' sobrecarregada.\nload: ', loadAverage[self.id])
            # print('CPU: ', self.cpuCoreCount)
            try:
                pass
                # print('eval =', evaluations[self.id])
            except:
                pass
            if (self.id in LoadBalancer.droped):
                LoadBalancer.droped[self.id] += 1
            else:
                LoadBalancer.droped[self.id] = 1
            dropou = True
            while(loadAverage[self.id] >= self.maxLoadAverage):
                time.sleep(10/1000.)

        if (dropou == False):
            # print('+5', self.id)
            with LoadBalancer._lock:
                loadAverage[self.id] += 5
                ramDisp[self.id] -= 10
                discoDisp[self.id] -= 100
                redeUtilizada[self.id] += 2

            if(loadAverage[self.id] >= self.limiteAceitavelLoadAvg):
                #fog sobrecarregada e penalizada com tempo
                self.aguardar = 10/1000.
                # self.aguardar = self.latency*0.5
                time.sleep(self.aguardar)
            time.sleep(self.latency)

            # if(loadAverage[self.id] != 0):
            with LoadBalancer._lock:
                loadAverage[self.id] -= 5
                ramDisp[self.id] += 10
                discoDisp[self.id] += 100
                redeUtilizada[self.id] -= 2
            #evaluations[self.id] = self.get
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
        if(loadAverage[self.id] == 0):
            return 1/1000
        else:
            return loadAverage[self.id]/self.cpuCoreCount

    def getEvaluation(self):
        if(self.loadAverage >= 90):
            e = 0
        if(ramDisp[self.id] <= (self.ram-(self.ram*0.9))):
            e = 0
        if(discoDisp[self.id] <= (self.storageAmount-(self.storageAmount*0.9))):
            e = 0
        else:
            e = ((self.cpuCoreCount*self.frequency)/((self.getLoadAverage()*100)/self.cpuCoreCount) + ramDisp[self.id]/100 + discoDisp[self.id]/1000)

        # evaluations[self.id] = e
        return e

    # def getBestFog(self):
        # if(len(evaluations)>0):
    #     return (max(evaluations))

    def getCpuCount(self):
        return self.cpuCoreCount

    def showState(self):
        if(ramDisp[self.id] < 20):
            with LoadBalancer._lock:
                print(  '\nid: ',self.id, '\ncpuCount:', self.cpuCoreCount,' load: ', self.getLoadAverage(),
                        '\nram: ',self.ram, ' ram disp: ', ramDisp[self.id],
                        '\nstorage: ', self.storageAmount, ' storage disp: ', discoDisp[self.id],
                        '\nrede: ', self.downloadbandwith, ' rede utilizada: ', redeUtilizada[self.id],
                        '\nLatency', self.latency, '\nfrequencia: ',self.frequency,
                        '\nevaluation: ', self.getEvaluation())
            # import os
            # print('\npid:', os.getpid())

