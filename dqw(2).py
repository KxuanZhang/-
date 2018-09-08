import csv
import re
import math


#实例
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
        self.destination = 0

#机器
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
        self.mubiaoinstance=[]

#App
class App:
    def __init__(self):
        self.App_id = 0
        self.App_cpu = []
        self.App_mem = []
        self.App_disk = 0
        self.App_p = 0
        self.App_m = 0
        self.App_pm = 0


"""cpu的占用比例上限，调参获取最佳"""
N = 1
x='e'
toApp = {}#App字典
dirAllMachine = {}  # 机器字典，包含全部的机器
dirAllApp = {}    #app字典，包含全部的app
dirAllInstance = {}  # 实例字典，包含全部的实例
result = {}  # 结果
allMachine = []
allInstance = []
overMachine = []  # 超了的机器
overInstance = []  # 已部署的实例
notMoveInstance = []  # 未移动的实例
conflictMachine = [] #初始化时app有冲突的机器


writer = csv.writer(open(x+'_ceshi3'+'0.68'+'_.csv', 'w', newline=''))
writer2 = csv.writer(open(x+x+'_ceshi3'+'0.68'+'_.csv', 'w', newline=''))



#判断cpu或memory是否超了,超了返回1
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
                    return 1
            else:
                if iNumber > iMaxNumber:
                    return 1
        elif name2 in toApp:
            insMaxNumber = int(toApp[name2])
            if insNumber >= insMaxNumber:
                return 1
    return 0

def yuedengyu(a,b):
    if abs(a-b)<1e-6:
        return 1
    else :
        return 0

#用来判断某一个实例是否可以放进机器之中
def putin(ins, mac):
    if ins.instance_disk <= mac.now_disk and ins.instance_p <= mac.now_p and ins.instance_m <= mac.now_m and ins.instance_pm <= mac.now_pm:
        if click(ins, mac) == 0:
            for i in range(98):
                if (ins.instance_cpu[i] > mac.now_cpu[i] and yuedengyu(ins.instance_cpu[i] , mac.now_cpu[i])!=1) or (ins.instance_mem[i] > mac.now_mem[i] and yuedengyu(ins.instance_mem[i] , mac.now_mem[i])!=1):
                    return 0
            return 1
        else:
            return 0
    else:
        return 0

def putin2(ins, mac):
    if ins.instance_disk <= mac.now_disk and ins.instance_p <= mac.now_p and ins.instance_m <= mac.now_m and ins.instance_pm <= mac.now_pm:
        if click(ins, mac) == 0:
            for i in range(98):
                if ins.instance_cpu[i] > mac.now_cpu[i] or ins.instance_mem[i] > mac.now_mem[i]:
                    print ("cpu mem limit")
                    return 0
            return 1
        else:
            print ("click")
            return 0
    else:
        print("resource limit")
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
    print(Mark,ins.instance_id,mac.machine_id)
    writer2.writerow([Mark,ins.instance_id, mac.machine_id])


def delete(waitForDelete):
    while waitForDelete:
        i = waitForDelete[0]
        waitForDelete.remove(i)
        if i[0] in i[1].instanceList:
            i[1].instanceList.remove(i[0])
        add(i[0],i[1])



#先找特殊的实例
readerMachine = (open('machine_resources.'+x+'.csv')).readlines()
specialMach = Machine()
rows = readerMachine[1]
row = rows.split(',')
specialMach.machine_cpu = float(row[1])
specialMach.machine_mem = float(row[2])
specialMach.now_disk = float(row[3])
specialMach.now_p = int(row[4])
specialMach.now_m = int(row[5])
specialMach.now_pm = int(row[6])


#先初始化app
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
        dirAllApp[str(app1.App_id)]=app1


#初始化machine
fileMachineResource = 'machine_resources.'+x+'.csv'
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
            mach1.now_cpu.append(float(mach1.machine_cpu) * N)
            mach1.now_mem.append(float(mach1.machine_mem))
        dirAllMachine[str(mach1.machine_id)]=mach1
        allMachine.append(mach1)


"""初始化toApp"""
fileAppInterface = 'app_interference.csv'
with open(fileAppInterface) as file:
    reader = csv.reader(file)
    for row in reader:
        appAAndB = row[0] + row[1]
        toApp[appAAndB] = row[2]


"""初始化Instance"""
fileInstancePre = 'instance_deploy.'+x+'.csv'
with open(fileInstancePre) as file:
    reader = csv.reader(file)
    for row in reader:
        inst1 = Instance()
        inst1.instance_id = row[0]
        inst1.App_id = row[1]
        appTemp = dirAllApp[str(inst1.App_id)]
        inst1.instance_cpu = appTemp.App_cpu
        inst1.instance_mem = appTemp.App_mem
        inst1.instance_disk = appTemp.App_disk
        inst1.instance_p = appTemp.App_p
        inst1.instance_m = appTemp.App_m
        inst1.instance_pm = appTemp.App_pm
        if row[2] != '':
            inst1.machine_id = row[2]
        dirAllInstance[str(inst1.instance_id)]=inst1
        allInstance.append(inst1)
        if row[2] != '':
            indexMa = dirAllMachine[row[2]]
            indexIn = dirAllInstance[str(row[0])]


#1
            if (click(indexIn, indexMa) == 1) and (indexMa not in conflictMachine) and (indexMa not in overMachine):#有冲突
            # if putin(indexIn, indexMa) == 0:#有冲突
                conflictMachine.append(indexMa)


            indexMa.now_disk -= indexIn.instance_disk
            indexMa.now_p -= indexIn.instance_p
            indexMa.now_m -= indexIn.instance_m
            indexMa.now_pm -= indexIn.instance_m
            indexMa.instanceList.append(indexIn)
            for i in range(98):
                indexMa.now_cpu[i] -= indexIn.instance_cpu[i]
                indexMa.now_mem[i] -= indexIn.instance_mem[i]

            if indexMa in conflictMachine:
                continue
#2
            if isMachineOver(indexMa) and (indexMa not in overMachine):
                overMachine.append(indexMa)
            if indexMa in overMachine:
                continue
#4
            overInstance.append(indexIn)

#初始化目标文件
fileInstancePre = x+'0.68_rest(1).csv'
with open(fileInstancePre) as file:
    reader = csv.reader(file)
    for row in reader:
        id=row[0]
        machine=dirAllMachine[row[1]]
        dirAllInstance[str(id)].destination=machine
        machine.mubiaoinstance.append(dirAllInstance[str(id)])
counts = 0

while counts<len(overInstance):
    i = overInstance[counts]
    for j in overMachine:
        if i in j.instanceList:
            overInstance.remove(i)
            counts -=1
            break
    counts += 1


Mark = 1
waitForDelete = []
moveinstance=[]
movemachine=[]
cannotmoveinstance=[]
emptymachine=[]
speinstance=[]
biginstance=[]
fullmachine=[]
a=[]
b=[]


#第一轮迁移
for i in allInstance:
    destmachine=i.destination
    if putin(i,destmachine)==1and i.machine_id!=destmachine.machine_id:
        moveinstance.append(i)
        z = dirAllMachine[i.machine_id]
        movemachine.append(z)
        move(i, destmachine)
    elif i.machine_id==destmachine.machine_id:
        continue
    else:
        cannotmoveinstance.append(i)


for i in range(len(moveinstance)):
    add(moveinstance[i],movemachine[i])
    movemachine[i].instanceList.remove(moveinstance[i])
moveinstance.clear()
movemachine.clear()

print ("no move"+str(len(cannotmoveinstance)))



number=0
for i in allMachine:
    d = 0
    for k in i.mubiaoinstance:
        if k not in i.instanceList:
            d=1
            break
    if d==0:
        number+=1
        fullmachine.append(i)
print ("full  "+str(len(fullmachine)))
Mark = 2
#第二轮迁移

thirdinstance=[]
while cannotmoveinstance:
    i=cannotmoveinstance[0]
    destmachine = i.destination
    if putin(i, destmachine) == 1 and i.machine_id != destmachine.machine_id:
        moveinstance.append(i)
        z = dirAllMachine[i.machine_id]
        movemachine.append(z)
        move(i, destmachine)
        cannotmoveinstance.remove(i)
    else:
        for k in fullmachine:
            if putin(i,k)==1:
                moveinstance.append(i)
                z = dirAllMachine[i.machine_id]
                movemachine.append(z)
                move(i, k)
                cannotmoveinstance.remove(i)
                thirdinstance.append(i)
                break
            elif k==fullmachine[len(fullmachine)-1] :
                speinstance.append(i)
                cannotmoveinstance.remove(i)
                print ("I can not move")
                print(i.instance_id,k.machine_id)
                break


for i in range(len(moveinstance)):
    add(moveinstance[i],movemachine[i])
    movemachine[i].instanceList.remove(moveinstance[i])
moveinstance.clear()
movemachine.clear()



print ("special2  "+str(len(speinstance)))
flag=0
for i in speinstance:
    for k in fullmachine:
        if putin(i,k)==1:
            moveinstance.append(i)
            z = dirAllMachine[i.machine_id]
            movemachine.append(z)
            move(i, k)
            flag=1
            break
    if flag==1:
        print ("wanna die")

print ("第三轮")
print (len(thirdinstance))
Mark = 3
#第三轮迁移
for i in thirdinstance:
    destmachine = i.destination
    if putin(i, destmachine)==1and i.machine_id!=destmachine.machine_id:
        moveinstance.append(i)
        z = dirAllMachine[i.machine_id]
        movemachine.append(z)
        move(i, destmachine)
    else:

        print("cannot "+i.instance_id,i.machine_id,destmachine.machine_id,destmachine.now_cpu,destmachine.now_mem,destmachine.now_disk)
        putin2(i,destmachine)
        for i in destmachine.instanceList:
            print (i.instance_id)

for i in range(len(moveinstance)):
    add(moveinstance[i],movemachine[i])
    movemachine[i].instanceList.remove(moveinstance[i])
moveinstance.clear()
movemachine.clear()

print ("special3  "+str(len(speinstance)))

while  speinstance:
    i=speinstance[0]
    destmachine = i.destination
    if putin(i, destmachine)==1and i.machine_id!=destmachine.machine_id:
        moveinstance.append(i)
        z = dirAllMachine[i.machine_id]
        movemachine.append(z)
        move(i, destmachine)
        speinstance.remove(i)
    elif i.machine_id==destmachine.machine_id:
        speinstance.remove(i)
    else:
        print("special cannot "+i.instance_id,i.machine_id,destmachine.machine_id,destmachine.now_cpu,destmachine.now_mem,destmachine.now_disk)
        putin2(i,destmachine)
        for i in destmachine.instanceList:
            print (i.instance_id)

for i in range(len(moveinstance)):
    add(moveinstance[i],movemachine[i])
    movemachine[i].instanceList.remove(moveinstance[i])
moveinstance.clear()
movemachine.clear()


writer.writerow([0,0])
for i in allInstance:
    writer.writerow([i.instance_id, i.machine_id])

