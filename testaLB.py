import threading as th
import numpy as np
from fogDevice import *
from sensor import *
from LoadBalancer import *

import random
import string



class TestaLB:
    def main(self):
        self.SENSORES = 10000
        self.FOGS = 10
        self.LATENCIASENSORES = 10/1000.
        self.PRIORIDADE = 1
        self.REQUISICOES = 1
        self.SLEEP = 0
        print("Começando o teste com " + str(self.SENSORES) +
                " sensores e " + str(self.FOGS) + " Nós de Fog.")
        fogs = list()
        for i in range(self.FOGS):
            l = (random.randint(1,80)/1000.)
            cpuCount = random.randint(1,4)
            freq = random.randint(8,25)*100
            ram = np.power(2,random.randint(1,11))
            disco = random.randint(1,80)*1000
            rede = random.randint(1,100)*10
            fogs.append(FogDeviceLB(i,'',cpuCount,ram,disco,10,rede,l,freq))

        self.lb = LoadBalancer(fogs, 1)
        sensores = list()

        for i in range(self.SENSORES):
            prio = random.randint(0,1)
            prioridade  = random.randint(0,1)
            sensores.append(Sensor(i,'',self.lb.id, self.LATENCIASENSORES, self.PRIORIDADE))

        threads = list()
        for s in sensores:
            t = th.Thread(target=self.run, args=(s,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

        for i in range(self.FOGS):
            aux = 0
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
            s.sendData(self.lb,s.getId(), s.getPriority(), s.getLatency, str)
            time.sleep(self.SLEEP)
t = TestaLB()
t.main()
