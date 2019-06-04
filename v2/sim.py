import queue
import random
import threading as th
import time


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

    times0 = dict()
    times1 = dict()
    CPU_history = dict()
    MEM_history = dict()
    NET_history = dict()
    DISK_history = dict()
    _printLock = th.Lock()
    _writeLock = th.Lock()

    def __init__(self, i):
        self.id = i

        self.cpuCount = 4           #random.randint(1, 8)            # numero de cores
        self.ramAmount = 2048       #2**random.randint(8, 13)       # Mb
        self.netCapacity = 100      #random.randint(10, 100)    # Mbps
        self.diskCapacity = 15000   #random.randint(8, 50)*1000 # Mb vai de 5 até 500GB
        self.CPU_freq = 1200        #random.randint(8, 21)*100      # Mhz

        self.CPU_history[self.id] = list()
        self.MEM_history[self.id] = list()
        self.NET_history[self.id] = list()
        self.DISK_history[self.id] = list()
        self.times0[self.id] = list()
        self.times1[self.id] = list()

    def doTask(self, task):
        self.tryCount += 1
        if self.canReceive():
            # startTime = time.time()
            startTime = task['bornTime']
            # self.receiveTask(task)
            self.processTask(task)

            self.sucessCount += 1
            endTime = time.time()
            self.elapsedTime = endTime - startTime
            if(task['priority'] == 0):
                self.times0[self.id].append(self.elapsedTime)
            if(task['priority'] == 1):
                self.times1[self.id].append(self.elapsedTime)
        else:
            self.dropsCount += 1

    def processTask(self, task):
        with self._writeLock:
            self.CPU += task['cpu'] / self.cpuCount
            self.MEM += (task['mem'] / self.ramAmount) * 100
            self.NET += (task['net'] / self.netCapacity) * 100
            self.DISK += (task['disk'] / self.diskCapacity) * 100
            self.evaluate(task)

        time.sleep(task['time'] / self.CPU_freq)

        if self.CPU > self.maxCPU * 0.9:
            time.sleep(random.randint(1, 50) / self.CPU_freq)

        j = random.randrange(0, task['jitter'])
        wait = (j + task['latency']) / 1000
        time.sleep(wait)

        self.CPU_history[self.id].append(self.CPU)
        self.MEM_history[self.id].append(self.MEM)
        self.NET_history[self.id].append(self.NET)
        self.DISK_history[self.id].append(self.DISK)

        with self._writeLock:
            self.CPU -= task['cpu'] / self.cpuCount
            self.MEM -= (task['mem'] / self.ramAmount) * 100
            self.NET -= (task['net'] / self.netCapacity) * 100
            self.DISK -= (task['disk'] / self.diskCapacity) * 100

    def receiveTask(self, task):
        self.NET += task['net']
        j = random.randrange(0, task['jitter'])
        wait = (j + task['latency']) / 1000
        time.sleep(wait)
        self.NET -= task['net']

    def canReceive(self):
        with self._writeLock:
            conditions = (self.CPU < self.maxCPU and
                          self.MEM < self.maxMEM and
                          self.NET < self.maxNET)
        return conditions

    def cpuAvg(self):
        try:
            avg = sum(self.CPU_history[self.id]) / len(self.CPU_history[self.id])
            return avg
        except:
            return 0

    def memAvg(self):
        try:
            avg = sum(self.MEM_history[self.id]) / len(self.MEM_history[self.id])
            return avg
        except:
            return 0

    def timeAvg0(self):
        try:
            return sum(self.times0[self.id]) / len(self.times0[self.id])
        except:
            return 0

    def timeAvg1(self):
        try:
            return sum(self.times1[self.id]) / len(self.times1[self.id])
        except:
            return 0


    def netAvg(self):
        try:
            return sum(self.NET_history[self.id]) / len(self.NET_history[self.id])
        except:
            return 0

    def diskAvg(self):
        try:
            return sum(self.DISK_history[self.id]) / len(self.DISK_history[self.id])
        except:
            return 0

    def dropRate(self):
        try:
            return self.dropsCount / self.tryCount
        except:
            return 0

    def evaluate(self, task):
        if (self.CPU > self.maxCPU * 0.9 or
            self.MEM > self.maxMEM * 0.9 or
            self.NET > self.maxNET * 0.9 or
            self.maxDISK * 0.9 < self.DISK):

            self.evaluation = 0
        else:
            r = ((self.cpuCount * self.CPU_freq)/self.CPU +
                    # (self.ramAmount-self.MEM)/100 +
                    (self.ramAmount * (self.MEM / 100)) / 100 +
                    # (self.diskCapacity-self.DISK)/1000)
                    (self.diskCapacity * (self.DISK/100)) / 1000)
            rede = ((self.netCapacity-self.NET) / (task['latency'] ** 2)) / (task['jitter'] ** 2)
        #except:
            #r = ((self.cpuCount * self.CPU_freq) +
            #     (self.ramAmount / 100) +
            #     self.diskCapacity / 1000)
            #rede = (self.netCapacity
            #        /((task['latency'] ** 2)
            #        /(task['jitter'] ** 2)))
            self.evaluation = r * rede
        return self.evaluation


class Fog:
    _lock = th.Lock()
    sending = False

    def __init__(self, dev):
        self.n = dev
        self.devices = [FogDevice(i) for i in range(dev)]
        self.q = queue.PriorityQueue()

    def queueTask(self, task):
        self.q.put(task)
        if (self.sending == False):
            self.LB = th.Thread(target=self.sendTask)
            self.LB.start()

    def sendTask(self):
        self.sending = True
        # print(self.q.qsize())
        while(self.q.empty() is False):
            # print(self.q.qsize())
            task = self.q.get().task
            # print(task)
            with self._lock:
                best_fog = self.getBestDevice(task)
            if self.devices[best_fog].canReceive():
                t = th.Thread(target=self.devices[best_fog].doTask, args=(task,))
                t.start()
            else:
                self.q.put(Task(task))
        self.sending = False

    def getBestDevice(self, task):
        # return random.randint(0, self.n-1)
        # return self.bestCpuAverage()
        # return self.bestDeviceAverage()
        return self.bestEderSchedule(task)

    def bestCpuAverage(self):
        avg = [d.CPU for d in self.devices]
        smaller = avg.index(min(avg))
        return self.devices[smaller].id

    def bestDeviceAverage(self):
        avg = [((d.CPU + d.MEM + d.NET) / 3) for d in self.devices]
        smaller = avg.index(min(avg))
        return smaller

    def bestEderSchedule(self, task):
        evaluates = [d.evaluation for d in self.devices]
        best = max(evaluates)
        choice = random.choice([i for i, v in enumerate(evaluates) if v == best])
        return choice

    def printDevicesStat(self):
        for d in self.devices:
            print('\ndevice', d.id,
                  '\nCores:', d.cpuCount, 'RAM:', d.ramAmount,
                  '\nCPU freq:', d.CPU_freq,
                  '\nNET:', d.netCapacity, 'Disk:', d.diskCapacity,
                  '\navgCPU: ', d.cpuAvg(), 'avg mem: ', d.memAvg(),
                  '\navgNET: ', d.netAvg(), 'avg disk: ', d.diskAvg(),
                  '\nDropRate: ', (d.dropRate())*100,
                  '\nTryCount:', d.tryCount,
                  '\nAvgTime0:', d.timeAvg0()*1000, ' ms',
                  '\nAvgTime1:', d.timeAvg1()*1000, ' ms')


class Sensor:

    def __init__(self, i, req):
        self.FREQ = random.randint(0, 30) / 1000
        # tempo entre requests em segundos
        self.REQUESTS = req  # num of requests
        self.ID = i
        priorityLevels = [0, 1]
        self.priority = random.choice(priorityLevels)

    def start(self, f):
        for i in range(self.REQUESTS):
            self.requestTask(f)
            time.sleep(self.FREQ)

    def requestTask(self, f):
        t = {'cpu': 5,       # 5% in one CPU core
                'mem': 5,       # Mb
                'disk': 30,     # Mb
                'net': 1,       # Mb
                'latency': 5,   # ms
                'jitter': 5,    # Random de 0 até 5
                'time': 30,     # em uma CPU de 1Ghz, demora 30ms
                'bornTime': time.time(),
                'priority': self.priority}
        task = Task(t)
        f.queueTask(task)
        # f.sendTask(task)

class Task:
    __slots__ = ('priority', 'task')

    def __init__(self, task):
        self.priority = task['priority']
        self.task = task

    def __lt__(self, other):
        return self.priority < other.priority

class Simulation:
    def __init__(self, sensors=100, fogs=5, requests=1000):
        self.SENSORES = sensors
        self.FOGS = fogs
        self.REQUESTS = requests
        self.f = Fog(self.FOGS)
        self.avgtime = int()
    def sim(self):
        sensors = [Sensor(i, self.REQUESTS) for i in range(self.SENSORES)]
        t = [th.Thread(target=s.start, args=(self.f,)) for s in sensors]
        [thread.start() for thread in t]
        self.f.LB.join()
        [thread.join() for thread in t]
        self.f.printDevicesStat()

    def timeResult(self):
        self.avgtime = [self.f.devices[i].timeAvg() for i in range(len(self.f.devices))]
        self.avgtime = sum(self.avgtime)/len(self.f.devices)
        return (self.avgtime*1000)

    def dropResult(self):
        self.avgDrops = [self.f.devices[i].dropRate() for i in range(len(self.f.devices))]
        self.avgDrops = sum(self.avgDrops)/len(self.f.devices)
        return self.avgDrops*100

def main():
    s = Simulation()
    s.sim()
    # s.timeResult()

if __name__== "__main__":
    main()
