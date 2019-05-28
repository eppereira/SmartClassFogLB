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

    times = dict()
    CPU_history = dict()
    MEM_history = dict()
    NET_history = dict()
    DISK_history = dict()
    _printLock = th.Lock()
    _writeLock = th.Lock()

    def __init__(self, i):
        self.id = i

        self.cpuCount = 4   #random.randint(1, 8)            # numero de cores
        self.ramAmount = 2048 # 2**random.randint(8, 13)       # Mb
        self.netCapacity = 100 # random.randint(1, 100)*10    # Mbps
        self.diskCapacity = 160000 # random.randint(8, 500)*1000 # Mb vai de 5 até 500GB
        self.CPU_freq = 1200 # random.randint(8, 21)*100      # Mhz

        self.CPU_history[self.id] = list()
        self.MEM_history[self.id] = list()
        self.NET_history[self.id] = list()
        self.DISK_history[self.id] = list()
        self.times[self.id] = list()

    def doTask(self, task):
        self.tryCount += 1
        if self.canReceive():
            startTime = time.time()

            # self.receiveTask(task)
            self.processTask(task)

            self.sucessCount += 1
            endTime = time.time()
            self.elapsedTime = endTime - startTime
            self.times[self.id].append(self.elapsedTime)
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

    # noinspection PyBroadException
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

    # noinspection PyBroadException
    def timeAvg(self):
        try:
            return sum(self.times[self.id]) / len(self.times[self.id])
        except:
            return 0

    # noinspection PyBroadException
    def netAvg(self):
        try:
            return sum(self.NET_history[self.id]) / len(self.NET_history[self.id])
        except:
            return 0

    # noinspection PyBroadException
    def diskAvg(self):
        try:
            return sum(self.DISK_history[self.id]) / len(self.DISK_history[self.id])
        except:
            return 0

    # noinspection PyBroadException
    def dropRate(self):
        try:
            return self.dropsCount / self.tryCount
        except:
            return 0

    def evaluate(self, task):
        if (self.CPU > self.maxCPU * 0.9 and
            self.MEM > self.maxMEM * 0.9 and
            self.NET > self.maxNET * 0.9 and
            self.maxDISK * 0.9 < self.DISK):

            self.evaluation = 0
        else:
            try:
                r = ((self.cpuCount * self.CPU_freq)/self.CPU +
                     (self.ramAmount * (self.MEM / 100)) / 100 +
                     (self.diskCapacity * (self.DISK/100)) / 1000)
                rede = (self.netCapacity * (self.NET / 100)
                         / ((task['latency'] ** 2)
                        / (task['jitter'] ** 2)))
            except:
                r = ((self.cpuCount * self.CPU_freq) +
                     (self.ramAmount / 100) +
                     self.diskCapacity / 1000)
                rede = (self.netCapacity
                        /((task['latency'] ** 2)
                        /(task['jitter'] ** 2)))
            finally:
                self.evaluation = r * rede
        return self.evaluation


class Fog:
    _lock = th.Lock()

    def __init__(self, dev):
        self.n = dev
        self.devices = [FogDevice(i) for i in range(dev)]

    def sendTask(self, task):
        with self._lock:
            best_fog = self.getBestDevice(task)
        self.devices[best_fog].doTask(task)
        # self.devices[best_fog].processTask(task)

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

    # noinspection PyBroadException
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
                  '\nDropRate: ', (d.dropRate()),
                  '\nTryCount:', d.tryCount,
                  '\nAvgTime:', d.timeAvg())


class Sensor:

    def __init__(self, i):
        self.DATA_LEN = 1024
        self.CPU_USE = 5  # %
        self.FREQ = random.randint(0, 100) / 1000
        # tempo entre requests em segundos
        self.REQUESTS = 1  # num of requests
        self.ID = i

    def start(self, f):
        for i in range(self.REQUESTS):
            self.requestTask(f)
            time.sleep(self.FREQ)

    def requestTask(self, f):
        task = {'cpu': 5,       # 5% in one CPU core
                'mem': 5,       # Mb
                'disk': 30,     # Mb
                'net': 1,       # Mb
                'latency': 15,  # ms
                'jitter': 5,    # Random de 0 até 5
                'time': 30}     # em uma CPU de 1Ghz, demora 30ms
        f.sendTask(task)


class Simulation:
    def __init__(self):
        self.SENSORES = 500
        self.FOGS = 2

    def sim(self):
        f = Fog(self.FOGS)
        sensors = [Sensor(i) for i in range(self.SENSORES)]
        t = [th.Thread(target=s.start, args=(f,)) for s in sensors]
        [thread.start() for thread in t]
        [thread.join() for thread in t]
        f.printDevicesStat()


s = Simulation()
s.sim()
