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
    queueTimes0 = dict()
    queueTimes1 = dict()
    lbTimes0 = dict()
    lbTimes1 = dict()

    CPU_history = dict()
    MEM_history = dict()
    NET_history = dict()
    DISK_history = dict()
    _printLock = th.Lock()
    _writeLock = th.Lock()

    def __init__(self, i, res):
        self.id = i
        self.cpuCount = res['CPU_count']        # numero de cores
        self.ramAmount = res['MEM']             # Mb
        self.netCapacity = res['NET']           # Mbps
        self.diskCapacity = res['DISK']         # Mb
        self.CPU_freq = 1200                    # Mhz
        self.latency = res['latency']
        self.jitter = res['jitter']

        self.CPU_history[self.id] = list()
        self.MEM_history[self.id] = list()
        self.NET_history[self.id] = list()
        self.DISK_history[self.id] = list()
        self.times0[self.id] = list()
        self.times1[self.id] = list()

        self.lbTimes0[self.id] = list()
        self.lbTimes1[self.id] = list()

        self.queueTimes0[self.id] = list()
        self.queueTimes1[self.id] = list()


    def doTask(self, task):
        self.tryCount += 1
        if self.canReceive():
            startTime = task['times']['bornTime']
            task['times']['processStart'] = time.time()
            self.processTask(task)

            self.sucessCount += 1
            endTime = time.time()
            self.elapsedTime = task['times']['processEnd'] - task['times']['processStart']
            self.queueTime = task['times']['dequeueTime'] - task['times']['enqueueTime']
            self.lbTime = task['times']['processStart'] - task['times']['dequeueTime']

            if (task['priority'] == 0):
                self.times0[self.id].append(self.elapsedTime)
                self.queueTimes0[self.id].append(self.queueTime)
                self.lbTimes0[self.id].append(self.lbTime)
            if (task['priority'] == 1):
                self.times1[self.id].append(self.elapsedTime)
                self.queueTimes1[self.id].append(self.queueTime)
                self.lbTimes1[self.id].append(self.lbTime)
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
            time.sleep(random.randint(1, 100) / self.CPU_freq)

        j = random.randrange(0, self.jitter)
        wait = (j + self.latency) / 1000
        # time.sleep(wait)

        self.CPU_history[self.id].append(self.CPU)
        self.MEM_history[self.id].append(self.MEM)
        self.NET_history[self.id].append(self.NET)
        self.DISK_history[self.id].append(self.DISK)

        with self._writeLock:
            self.CPU -= task['cpu'] / self.cpuCount
            self.MEM -= (task['mem'] / self.ramAmount) * 100
            self.NET -= (task['net'] / self.netCapacity) * 100
            self.DISK -= (task['disk'] / self.diskCapacity) * 100
        task['times']['processEnd'] = time.time()


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
        '''
        if conditions:
            print(time.time() - t1)
        '''
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

    def timeAvg(self):
        try:
            return [sum(self.times0[self.id]) / len(self.times0[self.id]),
                    sum(self.times1[self.id]) / len(self.times1[self.id])]
        except:
            return 0

    def timeLB0(self):
        try:
            return (sum(self.lbTimes0[self.id]) / len(self.lbTimes0[self.id]))
        except:
            return 0

    def TimeLB1(self):
        try:
            return (sum(self.lbTimes1[self.id]) / len(self.lbTimes1[self.id]))
        except:
            return 0

    def queueAvg0(self):
        try:
            return (sum(self.queueTimes0[self.id]) / len(self.queueTimes0[self.id]))
        except:
            return 0

    def queueAvg1(self):
        try:
            return (sum(self.queueTimes1[self.id]) / len(self.queueTimes1[self.id]))
        except:
            return 0

    def lbAvg0(self):
        try:
            return (sum(self.lbTimes0[self.id]) / len(self.lbTimes0[self.id]))
        except:
            return 0

    def lbAvg1(self):
        try:
            return (sum(self.lbTimes1[self.id]) / len(self.lbTimes1[self.id]))
        except:
            return 0

    def timeAvg0(self):
        try:
            return (sum(self.times0[self.id]) / len(self.times0[self.id]))
        except:
            return 0

    def timeAvg1(self):
        try:
            return (sum(self.times1[self.id]) / len(self.times1[self.id]))
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
            r = ((self.cpuCount * self.CPU_freq) / self.CPU +
                 (self.ramAmount * (self.MEM / 100)) / 100 +
                 (self.diskCapacity * (self.DISK / 100)) / 1000)

            rede = ((self.netCapacity - self.NET) / (self.latency ** 2)) / (self.jitter ** 2)
            self.evaluation = r * rede

        return self.evaluation


class Fog:
    _lock = th.Lock()
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
                task = self.q.get().task
                task['times']['dequeueTime'] = time.time()
                t = th.Thread(target=self.devices[best_fog].doTask, args=(task,))
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

    def __init__(self, i, req):
        # self.FREQ = random.randint(0, 300) / 1000
        self.FREQ = 50/1000
        # tempo entre requests em milisegundos
        self.REQUESTS = req  # num of requests
        self.ID = i
        priorityLevels = [0, 1]
        self.priority = random.choice(priorityLevels)

    def start(self, f):
        for i in range(self.REQUESTS):
            self.requestTask(f)
            time.sleep(self.FREQ)

    def requestTask(self, f):
        executionTime = {
            'bornTime': time.time(),
            'enqueueTime': None,
            'dequeueTime': None,
            'processStart': None,
            'ProcessEnd': None
        }
        taskResources = {
            'soft':{
                'cpu': 10,  # 5% in one CPU core
                'mem': 20,  # Mb
                'disk': 100,  # Mb
                'net': 1,  # Mb
                'time': 30,  # em uma CPU de 1Ghz, demora 30ms
                'times': executionTime,
                'priority': self.priority},
            'medium':{
                'cpu': 20,  # 5% in one CPU core
                'mem': 50,  # Mb
                'disk': 500,  # Mb
                'net': 1,  # Mb
                'time': 30,  # em uma CPU de 1Ghz, demora 30ms
                'times': executionTime,
                'priority': self.priority},
            'hard':{
                'cpu': 30,  # 5% in one CPU core
                'mem': 100,  # Mb
                'disk': 800,  # Mb
                'net': 1,  # Mb
                'time': 30,  # em uma CPU de 1Ghz, demora 30ms
                'times': executionTime,
                'priority': self.priority},
        }
        task = Task(taskResources['soft'])
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
    def __init__(self, sensors, fogs, fogResources='large', requests=100):
        self.SENSORES = sensors
        self.REQUESTS = requests
        self.f = Fog(fogs, res=fogResources)
        self.avgtime0 = int()
        self.avgtime1 = int()
        self.avgtime0 = int()
        self.avgtime1 = int()

    def sim(self):
        sensors = [Sensor(i, self.REQUESTS) for i in range(self.SENSORES)]
        t = [th.Thread(target=s.start, args=(self.f,)) for s in sensors]
        [thread.start() for thread in t]
        # self.f.LB.join()
        [thread.join() for thread in t]
        # self.f.printDevicesStat()

    def processTimeResult(self):
        self.avgtime0 = [self.f.devices[i].timeAvg0() for i in range(len(self.f.devices))]
        self.avgtime0 = (sum(self.avgtime0) / len(self.f.devices))*1000

        self.avgtime1 = [self.f.devices[i].timeAvg1() for i in range(len(self.f.devices))]
        self.avgtime1 = (sum(self.avgtime1) / len(self.f.devices))*1000

        return [self.avgtime0, self.avgtime1]

    def lbTimeResult(self):
        self.avgtime0 = [self.f.devices[i].lbAvg0() for i in range(len(self.f.devices))]
        self.avgtime0 = (sum(self.avgtime0) / len(self.f.devices))*1000

        self.avgtime1 = [self.f.devices[i].lbAvg1() for i in range(len(self.f.devices))]
        self.avgtime1 = (sum(self.avgtime1) / len(self.f.devices))*1000

        return [self.avgtime0, self.avgtime1]

    def queueTimeResult(self):
        self.avgtime0 = [self.f.devices[i].queueAvg0() for i in range(len(self.f.devices))]
        self.avgtime0 = (sum(self.avgtime0) / len(self.f.devices))*1000

        self.avgtime1 = [self.f.devices[i].queueAvg1() for i in range(len(self.f.devices))]
        self.avgtime1 = (sum(self.avgtime1) / len(self.f.devices))*1000

        return [self.avgtime0, self.avgtime1]

    def dropResult(self):
        self.avgDrops = [self.f.devices[i].dropRate() for i in range(len(self.f.devices))]
        self.avgDrops = sum(self.avgDrops) / len(self.f.devices)
        return self.avgDrops * 100


def main():
    s = Simulation()
    s.sim()
    print(s.timeResult())


if __name__ == "__main__":
    main()
