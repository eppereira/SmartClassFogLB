import threading as th
import numpy as np
import random
import time
import statistics
import operator

class FogDevice:
    CPU = 0 # 0 to 100%
    MEM = 0 # 0 to 100%
    NET = 0 # 0 to 100%
    
    maxCPU = 100
    maxMEM = 100
    maxNET = 100

    dropsCount = 0
    sucessCount = 0
    tryCount = 0
    times = dict()
    CPU_history = dict()
    MEM_history = dict()
    _printLock = th.Lock()
    _writeLock = th.Lock()

    def __init__(self, i):
        self.cpuCount = 1
        self.ramAmount = 1024
        self.netCapacity = 10
        self.id = i
        self.CPU_history[self.id] = list()
        self.MEM_history[self.id] = list()
        self.times[self.id] = list()
    def doTask(self, task):
        self.tryCount += 1
        startTime = time.time()
        time.sleep(random.randint(0,10)/100) # Setup time
        if self.canReceive():
            # self.receiveTask(task)
            self.processTask(task)
            self.sucessCount += 1
        else:
            self.dropsCount += 1
        endTime = time.time()
        self.elapsedTime = endTime-startTime
        self.times[self.id].append(self.elapsedTime)

    def processTask(self, task):
        with self._writeLock:
            self.CPU += task['cpu']
            self.MEM += task['mem']
            
        time.sleep(task['time']/1000)
        if self.CPU > self.CPU*0.9:
            time.sleep(random.randint(0,10)/1000)

        with self._writeLock:
            self.CPU -= task['cpu']
            self.MEM -= task['mem']

        self.CPU_history[self.id].append(self.CPU)
        self.MEM_history[self.id].append(self.MEM)

    def receiveTask(self, task):
        self.NET += task['net']
        j = random.randrange(0,task['jitter'])
        wait = (j + task['latency'])/1000
        time.sleep(wait)
        self.NET -= task['net']

    def canReceive(self):
        with self._writeLock:
            conditions = (  self.CPU < self.maxCPU and
                            self.MEM < self.maxMEM and
                            self.NET < self.maxNET)
        return conditions
    def cpuAvg(self):
        return sum(self.CPU_history[self.id])/len(self.CPU_history[self.id])
    def memAvg(self):
        return sum(self.MEM_history[self.id])/len(self.MEM_history[self.id])
    def timeAvg(self):
        return sum(self.times[self.id])/len(self.times[self.id])

class Fog:
    _lock = th.Lock()
    def __init__(self, dev):
        self.n = dev
        self.devices = [FogDevice(i) for i in range(dev)]
    def sendTask(self, task):
        with self._lock:
            best_fog = self.getBestDevice()
        self.devices[best_fog].doTask(task)
        # self.devices[best_fog].processTask(task)
    def getBestDevice(self):
        # return random.randint(0, self.n-1)
        # return self.bestCpuAverage()
        return self.bestDeviceAverage()

    def bestCpuAverage(self):
        avg = [((d.CPU)) for d in self.devices]
        smaller = avg.index(min(avg))
        return self.devices[smaller].id
    def bestDeviceAverage(self):
        # best = self.device[0]
        avg = [((d.CPU+d.MEM+d.NET)/3) for d in self.devices]
        smaller = avg.index(min(avg))
        return self.devices[smaller].id

    def printDevicesStat(self):
        for d in self.devices:
            print(  '\ndevice', d.id,
                    # '\ncpu:', d.CPU, 'mem:', d.MEM,
                    # '\nmax cpu: ', d.maxCPU, 'max mem: ', d.maxMEM,
                    '\navgCPU: ', d.cpuAvg(), 'avg mem: ', d.memAvg(),
                    '\nDropRate: ', (d.dropsCount/d.tryCount),
                    '\nTryCount:', d.tryCount,
                    '\nAvgTime:', d.timeAvg())
class Sensor:
    def __init__(self,i):
        self.DATA_LEN = 1024
        self.CPU_USE = 5 #%
        self.FREQ = 1 # tempo entre requests em segundos
        self.REQUESTS = 1 # num of requests
        self.ID = i
    def start(self, f):
        for i in range(self.REQUESTS):
            self.requestTask(f)
            time.sleep(self.FREQ)

    def requestTask(self, f):
        task = {'cpu': 5,
                'mem':5,
                'net':.5,
                'latency':15, # ms
                'jitter':5, # ms
                'time':30} # ms
        f.sendTask(task)
        
class Simulation:
    def __init__(self):
        self.SENSORES = 1000
        self.FOGS = 10
    def sim(self):
        f = Fog(self.FOGS)
        # TODO verificar as threads
        sensors = [Sensor(i) for i in range(self.SENSORES)]
        t = [th.Thread(target=s.start, args=(f,)) for s in sensors]
        for thread in t:
            thread.start()
        for thread in t:
            thread.join()
        f.printDevicesStat()
s = Simulation()
s.sim()

