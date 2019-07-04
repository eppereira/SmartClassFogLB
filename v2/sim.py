import queue
import random
import threading as th
import multiprocessing as mp
import time
import csv
import json

class FogDevice:
    CPU = 0  # 0 to 100%
    MEM = 0  # 0 to 100%
    NET = 0  # 0 to 100%
    DISK = 0

    maxCPU = 100
    maxMEM = 100
    maxNET = 100
    maxDISK = 100

    dropsCount = 0
    sucessCount = 0
    tryCount = 0

    evaluation = 100000

    _printLock = mp.Lock()
    _writeLock = mp.Lock()

    def __init__(self, i, res):
        self.id = i
        self.cpuCount = res['CPU_count']        # numero de cores
        self.ramAmount = res['MEM']             # Mb
        self.netCapacity = res['NET']           # Mbps
        self.diskCapacity = res['DISK']         # Mb
        self.CPU_freq = 1200                    # Mhz
        self.latency = res['latency']
        self.jitter = res['jitter']

    def doTask(self, task):
        self.tryCount += 1
        if self.canReceive():
            startTime = task['times']['bornTime']
            task['times']['processStart'] = time.time()
            self.processTask(task)

            self.sucessCount += 1
            endTime = time.time()
        else:
            self.dropsCount += 1

    def processTask(self, task):
        with self._writeLock:
            self.CPU += task['cpu'] / self.cpuCount
            self.MEM += (task['mem'] / self.ramAmount) * 100
            self.NET += (task['net'] / self.netCapacity) * 100
            self.DISK += (task['disk'] / self.diskCapacity) * 100
            self.evaluate(task)

        task['info']['fog'] = self.id
        time.sleep(task['time'] / self.CPU_freq)

        if self.CPU > self.maxCPU * 0.9:
            time.sleep(random.randint(1, 100) / self.CPU_freq)

        j = random.randrange(0, self.jitter)
        wait = (j + self.latency) / 1000
        # time.sleep(wait)

        task['times']['processEnd'] = time.time()

        with self._writeLock:
            self.CPU -= task['cpu'] / self.cpuCount
            self.MEM -= (task['mem'] / self.ramAmount) * 100
            self.NET -= (task['net'] / self.netCapacity) * 100
            self.DISK -= (task['disk'] / self.diskCapacity) * 100
        try:
            with open((task['info']['id_teste']), 'a') as f:
                f.write(json.dumps(task, indent=4))
        except:
            with open((task['info']['id_teste']), 'w') as f:
                f.write(json.dumps(task, indent=4))

    def receiveTask(self, task):
        self.NET += task['net']
        j = random.randrange(0, self.jitter)
        wait = (j + self.latency) / 1000
        time.sleep(wait)
        self.NET -= task['net']

    def canReceive(self):
        t1 = time.time()
        with self._writeLock:
            conditions = (self.CPU < self.maxCPU and
                          self.MEM < self.maxMEM and
                          self.NET < self.maxNET)
        return conditions

    def evaluate(self, task):
        if (self.CPU > self.maxCPU * 0.9 or
                self.MEM > self.maxMEM * 0.9 or
                self.NET > self.maxNET * 0.9 or
                self.maxDISK * 0.9 < self.DISK):

            self.evaluation = 0
        else:
            r = ((self.cpuCount * self.CPU_freq) / self.CPU +
                 (self.ramAmount * (self.MEM / 100)) / 100 +
                 (self.diskCapacity * (self.DISK / 100)) / 1000)

            rede = ((self.netCapacity - self.NET) / (self.latency ** 2)) / (self.jitter ** 2)
            self.evaluation = r * rede

        return self.evaluation


class Fog:
    _lock = mp.Lock()
    sending = False

    def __init__(self, dev, res):
        self.n = dev
        self.fogResources = {
            'small':{
                    'CPU_count': 1,
                    'MEM': 512,
                    'DISK': 2048,
                    'NET': 50,
                    'latency': 10,
                    'jitter': 5},

            'medium':{
                    'CPU_count': 2,
                    'MEM': 1024,
                    'DISK': 4096,
                    'NET': 80,
                    'latency': 10,
                    'jitter': 5},

            'large':{
                    'CPU_count': 4,
                    'MEM': 2048,
                    'DISK': 10240,
                    'NET': 100,
                    'latency': 10,
                    'jitter': 5}
        }
        if (res=='mixed'):
            self.devices = [FogDevice(i, self.fogResources['small']) for i in range(self.n//3)]
            self.devices+= [FogDevice((i+self.n//3), self.fogResources['medium']) for i in range(self.n//3)]
            self.devices+= [FogDevice((i+(2*self.n)//3), self.fogResources['large']) for i in range(self.n//3)]
        else:
            self.devices = [FogDevice(i, self.fogResources[res]) for i in range(dev)]
        self.q = queue.PriorityQueue()

    def queueTask(self, task):
        self.q.put(task)

        if (self.sending == False):
            # self.LB = th.Thread(target=self.sendTask)
            # self.LB.start()
            self.sendTask()

    def sendTask(self):
        self.sending = True
        # print(self.q.qsize())
        while (self.q.empty() is False):
            with self._lock:
                best_fog = self.getBestDevice() # TODO: definir a escolha da fog para tarefas nao prioritarias
            if self.devices[best_fog].canReceive():
                # print(str(self.q.qsize())+ '\n')

                qsize = self.q.qsize()
                task = self.q.get().task
                task['times']['dequeueTime'] = time.time()
                task['times']['queueLength'] = qsize
                # print(qsize)
                # t = th.Thread(target=self.devices[best_fog].doTask, args=(task,))
                t = mp.Process(target=self.devices[best_fog].doTask, args=(task,))
                t.start()
                # self.devices[best_fog].doTask(task)
        self.sending = False

    def getBestDevice(self):
        return self.bestEderSchedule()

    def bestCpuAverage(self):
        avg = [d.CPU for d in self.devices]
        smaller = avg.index(min(avg))
        return self.devices[smaller].id

    def bestDeviceAverage(self):
        avg = [((d.CPU + d.MEM + d.NET) / 3) for d in self.devices]
        smaller = avg.index(min(avg))
        return smaller

    def bestEderSchedule(self):
        evaluates = [d.evaluation for d in self.devices]
        best = max(evaluates)
        choice = random.choice([i for i, v in enumerate(evaluates) if v == best])
        # quando existem mais de um dispositivo com a mesma nota e escolhido aleatoriamente
        return choice

    def printDevicesStat(self):
        for d in self.devices:
            print('\ndevice', d.id,
                    '\nCores:', d.cpuCount, 'RAM:', d.ramAmount,
                    '\nCPU freq:', d.CPU_freq,
                    '\nNET:', d.netCapacity, 'Disk:', d.diskCapacity,
                    '\navgCPU: ', d.cpuAvg(), 'avg mem: ', d.memAvg(),
                    '\navgNET: ', d.netAvg(), 'avg disk: ', d.diskAvg(),
                    '\nDropRate: ', (d.dropRate()) * 100,
                    '\nTryCount:', d.tryCount
                    # '\nAvgTime0:', (d.timeAvg())*1000, ' ms',
                    # '\nAvgTime1:', (d.timeAvg())*1000, ' ms'
            )


class Sensor:

    def __init__(self, i, req, taskType, id_teste):
        # self.FREQ = random.randint(0, 300) / 1000
        self.FREQ = 100/1000
        # tempo entre requests em milisegundos
        self.REQUESTS = req  # num of requests
        self.ID = i
        self.taskType = taskType
        self.id_teste = id_teste
        priorityLevels = [0, 1]
        self.priority = priorityLevels[i%2]

    def run(self, f):
        for i in range(self.REQUESTS):
            self.requestTask(f, i)
            time.sleep(self.FREQ)

    def requestTask(self, f, i):
        executionTime = {
            'bornTime': time.time(),
            'enqueueTime': None,
            'dequeueTime': None,
            'processStart': None,
            'processEnd': None,
            'queueLength': None
        }
        info = {
            'sensor': self.ID,
            'seq': i,
            'fog': None,
            'id_teste': self.id_teste
            }
        taskResources = {
            'soft':{
                'cpu': 10,      # in one CPU core
                'mem': 20,      # Mb
                'disk': 100,    # Mb
                'net': 1,       # Mb
                'time': 30,     # em uma CPU de 1Ghz, demora 30ms
                'times': executionTime,
                'info': info,
                'priority': self.priority},
            'medium':{
                'cpu': 20,      # in one CPU core
                'mem': 50,      # Mb
                'disk': 500,    # Mb
                'net': 1,       # Mb
                'time': 30,     # em uma CPU de 1Ghz, demora 30ms
                'times': executionTime,
                'info': info,
                'priority': self.priority},
            'hard':{
                'cpu': 30,      # in one CPU core
                'mem': 100,     # Mb
                'disk': 800,    # Mb
                'net': 1,       # Mb
                'time': 30,     # em uma CPU de 1Ghz, demora 30ms
                'times': executionTime,
                'info': info,
                'priority': self.priority},
        }
        task = Task(taskResources[self.taskType])
        task.task['times']['enqueueTime'] = time.time()
        f.queueTask(task)


class Task:
    __slots__ = ('priority', 'task')

    def __init__(self, task):
        self.priority = task['priority']
        self.task = task

    def __lt__(self, other):
        return self.priority < other.priority


class Simulation:
    def __init__(self, sensors, taskResource, fogs, fogResources='large', requests=100):
        self.SENSORES = sensors
        self.REQUESTS = requests
        self.f = Fog(fogs, res=fogResources)
        self.taskResource = taskResource

    def sim(self, id_teste):
        if self.taskResource == 'mixed':
            # print(type(self.SENSORES))
            sensors =  [Sensor(i, self.REQUESTS, 'soft', id_teste) for i in range(self.SENSORES//3)]
            sensors+=[Sensor((i+self.SENSORES//3), self.REQUESTS, 'medium', id_teste) for i in range(self.SENSORES//3)]
            sensors+=[Sensor((i+(2*self.SENSORES)//3), self.REQUESTS, 'hard', id_teste) for i in range(self.SENSORES//3)]
            # t = [th.Thread(target=s.start, args=(self.f,)) for s in sensors]

        else:
            sensors = [Sensor(i, self.REQUESTS, self.taskResource, id_teste) for i in range(self.SENSORES)]

        # t = [th.Thread(target=s.run, args=(self.f,)) for s in sensors]
        t = [mp.Process(target=s.run, args=(self.f,)) for s in sensors]
        [thread.start() for thread in t]
        # self.f.LB.join()
        [thread.join() for thread in t]
        # self.f.printDevicesStat()

def main():
    t0 = time.time()
    file = './result/teste 0'
    print('Start Time:',t0)
    f = open('testes.csv', 'r')
    tests = csv.reader(f)
    for test in tests:
        print(test[:4])
        simulations = [Simulation(sensors=180 ,taskResource=test[2], fogs=9, fogResources=test[1], requests=int(test[3]))]
        for s in simulations:
            s.sim(file)

    f.close()
    tf = time.time()
    print('elapsed time: ', (tf-t0))

def main2():
    t0 = time.time()
    print('Start Time:',t0)
    simulations = [Simulation(sensors=100 ,taskResource='soft', fogs=9, fogResources='large', requests=100)]
    for s in simulations:
        s.sim('0')
    tf = time.time()
    print('elapsed time: ', (tf-t0))
if __name__ == "__main__":
    main2()
