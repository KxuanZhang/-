import copy
import csv
import math
import datetime
import re
class Instance:
    def __init__(self):
        """初始化"""
        self.instance_id = 0
        self.App_id = 0
        self.machine_id = 0
        self.instance_cpu = []
        self.instance_mem = []
        self.instance_disk = 0
        self.instance_p = 0
        self.instance_m = 0
        self.instance_pm = 0

class Machine:
    def __init__(self):
        self.machine_id = 0
        self.machine_cpu = 0
        self.machine_mem = 0
        self.now_cpu = []
        self.now_mem = []
        self.now_disk = 0
        self.now_p = 0
        self.now_m = 0
        self.now_pm = 0
        self.instanceList = []
        self.maxUsedCpu = 0
        self.score = 0

class App:
    def __init__(self):
        self.App_id = 0
        self.App_cpu = []
        self.App_mem = []
        self.App_disk = 0
        self.App_p = 0
        self.App_m = 0
        self.App_pm = 0


initFile =  'dd0.5small(2).csv'



toApp = {}
interfaceToApp = {}

S = 'd'
N = 0.68
allInstance = []  #实例数组
allMachine = []   #机器数组
allApp = []
overMachine = []  #超了的机器
overInstance = []   #已部署的实例
notOverInstance = [] #未部署实例
result = {}     #result
notMoveInstance = [] # Instances that not move
dirAllMachine = {}
dirAllApp = {}
dirAllInstance = {}




def isCpuMemOver(list):
    for i in range(98):
        if list[i] < 0:
            return 1
    return 0

#判断机器的各项属性是否超了,超了返回1
def isMachineOver(mac):
    if mac.now_disk < 0 or mac.now_p < 0 or mac.now_m < 0 or mac.now_pm < 0:
        return 1
    elif isCpuMemOver(mac.now_cpu) or isCpuMemOver(mac.now_mem):
        return 1
    else:
        return 0

#计算某一个实例所属的app种类在某一个机器中已经存在的个数
def account(ins, mac):
    number = 0
    for i in mac.instanceList:
        if ins.App_id == i.App_id:
            number += 1
    return number

#1是no，用来判断实例在机器中的app种类问题
def click(ins, mac):
    for i in mac.instanceList:
        name1 = ins.App_id + i.App_id
        name2 = i.App_id + ins.App_id
        insNumber = account(ins, mac)
        iNumber = account(i, mac)
        if name1 in toApp:
            iMaxNumber = int(toApp[name1])
            if name2 in toApp:
                insMaxNumber = int(toApp[name2])
                if iNumber > iMaxNumber or insNumber >= insMaxNumber:
                    # print(ins.instance_id + ' ' + i.instance_id)
                    return 1
            else:
                if iNumber > iMaxNumber:
                    # print(ins.instance_id + ' ' + i.instance_id)
                    return 1
        elif name2 in toApp:
            insMaxNumber = int(toApp[name2])
            if insNumber >= insMaxNumber:
                # print(ins.instance_id + ' ' + i.instance_id)
                return 1
    return 0

#用来判断某一个实例是否可以放进机器之中
def putin(ins, mac):
    if ins.instance_disk <= mac.now_disk and ins.instance_p <= mac.now_p and ins.instance_m <= mac.now_m and ins.instance_pm <= mac.now_pm:
        if click(ins, mac) == 0:
            for i in range(98):
                if ins.instance_cpu[i] > mac.now_cpu[i] or ins.instance_mem[i] > mac.now_mem[i]:
                    return 0
            return 1
        else:
            return 0
    else:
        return 0

#把从mac移出的ins的所占用的各项属性都给加上
def add(ins, mac):
    mac.now_disk += ins.instance_disk
    mac.now_p += ins.instance_p
    mac.now_m += ins.instance_m
    mac.now_pm += ins.instance_pm
    for q in range(98):
        mac.now_cpu[q] += ins.instance_cpu[q]
        mac.now_mem[q] += ins.instance_mem[q]

#把ins移进mac中去
def move(ins, mac):
    mac.instanceList.append(ins)
    ins.machine_id = mac.machine_id
    mac.now_disk -= ins.instance_disk
    mac.now_p -= ins.instance_p
    mac.now_m -= ins.instance_m
    mac.now_pm -= ins.instance_pm
    for q in range(98):
        mac.now_cpu[q] -= ins.instance_cpu[q]
        mac.now_mem[q] -= ins.instance_mem[q]
    # print(ins.instance_id, mac.machine_id)

#判断此时mac是否符合要求,符合要求返回1，否则返回0
def isMachineOk(mac):
    tempMac = Machine()
    tempMac.machine_cpu = mac.machine_cpu
    tempMac.machine_mem = mac.machine_mem
    tempMac.now_disk = mac.now_disk
    tempMac.now_m = mac.now_m
    tempMac.now_p = mac.now_p
    tempMac.now_pm = mac.now_pm
    for i in range(98):
        tempMac.now_cpu.append(tempMac.machine_cpu * N)
        tempMac.now_mem.append(tempMac.machine_mem)

    for ins in mac.instanceList:
        if click(ins,tempMac):
            print( 'click' +ins.instance_id)
            return 0
        print(ins.instance_id)
        tempMac.instanceList.append(ins)

        tempMac.now_disk -= ins.instance_disk
        tempMac.now_p -= ins.instance_p
        tempMac.now_m -= ins.instance_m
        tempMac.now_pm -= ins.instance_pm
        for q in range(98):
            tempMac.now_cpu[q] -= ins.instance_cpu[q]
            tempMac.now_mem[q] -= ins.instance_mem[q]
    if isMachineOver(tempMac):
        print('over')
        return 0
    return 1

def getN():
    low = 0
    for i in range(len(allMachine)-1,0,-1):
        if allMachine[i].maxUsedCpu > 0:
            low = i
            break
    return low


def getScore(mac):
    b = 0.5
    a = 1 + len(mac.instanceList)
    totalCostScore = 0
    for t in range(98):

            if a == 1:
                return 0
            c = (mac.machine_cpu  - mac.now_cpu[t]) / mac.machine_cpu
            # print(mac.now_cpu[t])
            # print('c' + str(c))
            s = 1 + a * (math.exp(max(0, c - b)) - 1)

            totalCostScore += s

    totalCostScore /= 98
    return totalCostScore

def addScore(ins, mac):

    if putin(ins, mac):
        b = 0.5
        a = 1 + len(mac.instanceList) +1
        totalCostScore = 0
        for t in range(98):

            if a == 1:
                return 0
            c = (mac.machine_cpu  - mac.now_cpu[t] + ins.instance_cpu[t]) / mac.machine_cpu
            s = 1 + a * (math.exp(max(0, c - b)) - 1)
            totalCostScore += s

        totalCostScore /= 98
        return  totalCostScore
    else:
        return 0


def subScore(ins , mac):
    b = 0.5
    a = 1 + len(mac.instanceList) - 1
    totalCostScore = 0
    for t in range(98):

        if a == 1:
            return 0
        c = (mac.machine_cpu - mac.now_cpu[t] - ins.instance_cpu[t]) / mac.machine_cpu
        s = 1 + a * (math.exp(max(0, c - b)) - 1)
        totalCostScore += s

    totalCostScore /= 98
    return totalCostScore


def average(mac1, mac2):
     score1 = getScore(mac1)
     score2 = getScore(mac2)
     before = score1 + score2
     # print(str(score1) + ' ' + str(score2))
     for ins in mac1.instanceList:
         score1 = float(getScore(mac1))
         score2 = float(getScore(mac2))

         if  float(addScore(ins, mac2)+ subScore(ins, mac1)) < score2 + score1:
             if putin(ins, mac2):
                 move(ins, mac2)
                 mac1.instanceList.remove(ins)
                 add(ins, mac1)
     for ins in mac2.instanceList:
         score1 = float(getScore(mac1))
         score2 = float(getScore(mac2))
         if  float(addScore(ins, mac1)+ subScore(ins, mac2)) < score2 + score1:
             if putin(ins, mac1):
                 move(ins, mac1)
                 mac2.instanceList.remove(ins)
                 add(ins, mac2)
     score1 = getScore(mac1)
     score2 = getScore(mac2)
     if score1 + score2 < before:
        print(str(score1) + ' then' + str(score2))
        return 1
     else:
         return 0


"""先初始化app"""
fileAppResource = 'app_resources.csv'
with open(fileAppResource) as f:
    reader = csv.reader(f)
    for row in reader:
        app1 = App()
        app1.App_id = row[0]
        app1.App_cpu = re.split('\|', row[1])
        for i in range(98):
            app1.App_cpu[i] = float(app1.App_cpu[i])
        app1.App_mem = re.split('\|', row[2])
        for i in range(98):
            app1.App_mem[i] = float(app1.App_mem[i])
        app1.App_disk = float(row[3])
        app1.App_p = int(row[4])
        app1.App_m = int(row[5])
        app1.App_pm = int(row[6])
        allApp.append(app1)
        dirAllApp[app1.App_id] = app1

"""初始化machine"""
fileMachineResource = 'machine_resources.'+S+'.csv'
with open(fileMachineResource) as file:
    reader = csv.reader(file)
    for row in reader:
        mach1 = Machine()
        mach1.machine_id = row[0]
        mach1.machine_cpu = float(row[1])
        mach1.machine_mem = float(row[2])
        mach1.now_disk = float(row[3])
        mach1.now_p = int(row[4])
        mach1.now_m = int(row[5])
        mach1.now_pm = int(row[6])
        for i in range(98):
                mach1.now_cpu.append(float(mach1.machine_cpu))
                mach1.now_mem.append(float(mach1.machine_mem))
        allMachine.append(mach1)
        dirAllMachine[mach1.machine_id] = mach1

"""初始化Instance"""
fileInstancePre =  'instance_deploy.'+S+'.csv'
with open(fileInstancePre) as file:
    reader = csv.reader(file)
    for row in reader:
        inst1 = Instance()
        inst1.instance_id = row[0]
        inst1.App_id = row[1]
        inst1.machine_id = row[2]
        appTemp = dirAllApp[inst1.App_id]
        inst1.instance_cpu = appTemp.App_cpu
        inst1.instance_mem = appTemp.App_mem
        inst1.instance_disk = appTemp.App_disk
        inst1.instance_p = appTemp.App_p
        inst1.instance_m = appTemp.App_m
        inst1.instance_pm = appTemp.App_pm
        allInstance.append(inst1)
        dirAllInstance[inst1.instance_id] = inst1


"""初始化toApp"""
fileAppInterface = 'app_interference.csv'
with open(fileAppInterface) as file:
    reader = csv.reader(file)
    for row in reader:
       appAAndB = row[0] + row[1]
       toApp[appAAndB] = row[2]


"""yongyong yong 初始化allMachine"""


with open(initFile) as file:
    reader = csv.reader(file)
    for row in reader:
        inst1 = dirAllInstance[row[1]]
        if row[2] != '':
            inst1.machine_id = row[2]




for ins1 in allInstance:
            indexMa = dirAllMachine[ins1.machine_id]
            indexMa.now_disk -= inst1.instance_disk
            indexMa.now_p -= inst1.instance_p
            indexMa.now_m -= inst1.instance_m
            indexMa.now_pm -= inst1.instance_m
            indexMa.instanceList.append(inst1)
            for i in range(98):
                indexMa.now_cpu[i] -= inst1.instance_cpu[i]
                indexMa.now_mem[i] -= inst1.instance_mem[i]


for i in allMachine:
    # print(i.now_cpu)
    maxCpu = i.machine_cpu - min(i.now_cpu)
    i.maxUsedCpu = float(maxCpu / i.machine_cpu)
    i.score = getScore(i)


allMachine =sorted(allMachine,key=lambda x:x.score ,reverse=True)


# count = 0
# for mac in allMachine:
#     if mac.maxUsedCpu == 0:
#         count += 1
#
# print(count)


lowN = 0
turn = 1

while True:
    lowN = getN()
    writerResult = csv.writer(open('turn' + initFile +str(turn) + '.csv', 'w', newline=''))
    for m1 in range(0 , lowN+1):
        print('turn' + str(turn) + ':' + str(m1))
        for m2 in range(lowN , m1 , -1):
            if m1 == m2:
                continue

            mac = allMachine[m1]
            mac2 = allMachine[m2]
            if average(mac, mac2) == 1:
                break

    for mac in allMachine:
        mac.score = getScore(mac)
    allMachine = sorted(allMachine, key=lambda x: x.score, reverse=True)
    for ins in allInstance:
        writerResult.writerow([ins.instance_id, ins.machine_id])

    turn += 1



