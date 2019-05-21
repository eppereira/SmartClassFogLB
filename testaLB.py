import threading as th
import numpy as np
from fogDevice import *
from sensor import *
from LoadBalancer import *

import random
import string

class TestaLB:
    def main(self):
        self.SENSORES = 100000
        self.FOGS = 10
        self.LATENCIASENSORES = 10/1000.
        self.PRIORIDADE = 1
        self.REQUISICOES = 1 #requisições por sensor
        self.SLEEP = 0.1 # tempo entre requisições do sensor
        print(  "Começando o teste com " + str(self.SENSORES) +
                " sensores e " + str(self.FOGS) + " Nós de Fog.")
        self.fogs = list()
        for i in range(self.FOGS):
            l = (random.randint(1,80)/1000.) # latency
            cpuCount = 1 # random.randint(1,4) # CPU Count
            freq = 1200 # random.randint(8,25)*100 # frequencia da cpu
            ram = 1024 # np.power(2,random.randint(1,11))
            disco = 4000 # random.randint(1,80)*1000
            rede = 10000 # random.randint(1,100)*10
            self.fogs.append(FogDeviceLB(i,'',cpuCount,ram,disco,10,rede,l,freq))

        self.lb = LoadBalancer()
        sensores = list()
        for i in range(self.SENSORES):
            # prioridade  = random.randint(0,1)
            sensores.append(Sensor(i,'', self.LATENCIASENSORES, self.PRIORIDADE))

        threads = list()
        for s in sensores:
            t = th.Thread(target=self.run, args=(s,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
        for i in range(self.FOGS):
            for e in LoadBalancer.encaminhados:
                if e == i:
                    enc = LoadBalancer.encaminhados[e]
                    print(e,' encaminou: ', enc)
            for d in LoadBalancer.droped:
                if d == i:
                    drop = LoadBalancer.droped[d]
                    print(d,' dropou: ', drop)

        media = 0
        n = 0
        for t in LoadBalancer.tempos:
            media += t
            n += 1
        media = media/n
        # print(LoadBalancer.tempos)

    def run(self, s):
        N = 10
        str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))
        for i in range(self.REQUISICOES):
            s.sendData(self.lb, s.getPriority(), s.getLatency, str, self.fogs)
            time.sleep(self.SLEEP)
t = TestaLB()
t.main()
