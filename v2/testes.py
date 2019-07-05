#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import statistics
import os

from sim import *


# In[2]:


def testa(file, fogType='mixed', taskType='mixed', nReq=100):
    # file = './result/teste 0'
    try:
        os.remove(file)
    except:
        pass

    t0 = time.time()
    print('Start Time:',time.strftime('%X'))
    simulations = [Simulation(sensors=70, taskResource=taskType, fogs=9, fogResources=fogType, requests=nReq)]
    for s in simulations:
        s.sim(file)
    tf = time.time()
    print('End Time:',time.strftime('%X'))
    print('elapsed time (s): ', (tf-t0))
    with open(file,'r') as f:
        data = f.read()
        data = "[" + data.replace("}{", "},{", data.count("}")-1) + "]"
        data = json.loads(data)

    with open(file, 'w') as f:
        f.write(json.dumps(data, indent=4))
    return data


# In[3]:


def mostra(data):
    totalTime0 = list()
    processTime0 = list()
    queueTime0 = list()
    queueLen = list()
    totalTime1 = list()
    processTime1 = list()
    queueTime1 = list()

    fogCount = dict()

    for t in data:
        tTime = t['times']['processEnd'] - t['times']['bornTime']
        pTime = t['times']['processEnd'] - t['times']['processStart']
        qTime = t['times']['processStart'] - t['times']['enqueueTime']
        qLen = t['times']['queueLength']
        queueLen.append(qLen)
        if t['priority'] == 0:
            totalTime0.append(tTime)
            processTime0.append(pTime)
            queueTime0.append(qTime)

        if t['priority'] == 1:
            totalTime1.append(tTime)
            processTime1.append(pTime)
            queueTime1.append(qTime)

        try:
            fogCount[t['info']['fog']] += 1
        except:
            fogCount[t['info']['fog']] = 1

    print('\nPRIORIDADE 0')
    print('tempo total', (sum(totalTime0)/len(totalTime0))*1000)
    print('tempo de processamento',(sum(processTime0)/len(processTime0)*1000))
    print('tempo de fila', sum(queueTime0)/len(queueTime0)*1000)
    print("processos com prioridade 0 = ", len(queueTime0))


    print('\nPRIORIDADE 1')
    print('tempo total', (sum(totalTime1)/len(totalTime1))*1000)
    print('tempo de processamento',(sum(processTime1)/len(processTime1)*1000))
    print('tempo de fila', sum(queueTime1)/len(queueTime1)*1000)
    print("processos com prioridade 1 = ", len(queueTime1))
    print('\nTamanho medio da fila:', sum(queueLen)/len(queueLen))
    print('\n\n')


# In[ ]:


with open('testes.csv', 'r') as csvFile:
    testes = csv.reader(csvFile)
    for teste in testes:
        print('\n' + str(teste))
        file = './result/teste '+teste[0]
        data = testa(file, teste[1], teste[2], int(teste[3]))
        mostra(data)
