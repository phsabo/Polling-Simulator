# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 16:19:40 2018

@author: PauloHenrique
"""
import numpy as np
import statistics
import matplotlib.pyplot as plt
import datetime
import csv

NodesBegin=1
NodesEnd=50
passo=1

InterMax=1500 #miliseconds
InterMed=1000
InterMin=100#miliseconds
ProcessingTime = 600 #segundos
ProcessingTime*=1000 #paramilisegundos,micro
SucessoTransmissao=100 #%
DistribuicaoIntervalos="poisson"# linear, poisson, exponential, normal
DisciplinaServico = "knowing" #FIFO, knowing, knowingstd, hibrid, random


velocidadeTransmissao = 250000 #250kbps
tamanhoPacote = 40 #bytes 1 preamble, 5 pipe, 32 payload, 2 CRC
airTime=(8*(tamanhoPacote)+9)/velocidadeTransmissao
timeUpload=(8*32)/400000
totalTime=airTime*2+timeUpload*4
time2=int(totalTime*1000)+1

ServerInterval = time2  # +-6
print("Serviço: ",ServerInterval)

DeltaDelay=2*ServerInterval#milisegundos

Nodes=10
AuxNode=0
Intervalos = np.zeros(Nodes)
IntervalosAcumul = np.zeros(Nodes)
listDelay=[]
lostPolls=0
lostMsgs=0
listMedianDelay=[]
listLostMsgs=[]
listSuccessPolls=[]
qtdeAmostras=5 #largura da tabela
listKnowing=np.zeros(1)
listTotalPolls=[]
listPollsWithoutResponse=[]
listPacketsProduced=[]
PacketsProduced=0
listPacketsSend=[]
PacketsSend=0
listTPolls=[]
TPolls=0

lastPoll=0
lastlastPoll=0

np.random.seed(1)
    
packets = np.zeros(Nodes)

print("Simulating")
now = datetime.datetime.now()
print('{:02d}'.format(now.hour)+":"+'{:02d}'.format(now.minute)+":"+'{:02d}'.format(now.second))
aux=0

def Polling(modo,now):
    global AuxNode
    global aux
    global lastPoll
    global lastlastPoll

    if(modo=="hibrid" and listKnowing.min()!=0):
        #média das diferenças
        dif=listKnowing[:, 1:]-listKnowing[:, :-1]
        l=np.mean(dif, axis=1).astype(int)
        #print(l)
        if (aux==Nodes*qtdeAmostras*2):
            listKnowing[:][-1]=0
            #print(dp)
            aux=0
            return -1
        nextTrans=l+listKnowing[:,-1]
        #print("next transmition "+str(nextTrans))
        l2=nextTrans-now+DeltaDelay#+np.random.randint(0,DeltaDelay*5,size=len(l))
        #print(l2)
        value=np.min(l2)
        #value=np.min(l2)
        #if(value<DeltaDelay and value>-(Nodes*DeltaDelay)):
        if(value<Nodes*DeltaDelay/10):
            #print(np.argmin(l2))
            aux=aux+1
            #print(aux,"h",end=' ')
            return np.argmin(l2)
        else:
            return -1
    if(modo=="knowingstd" and listKnowing.min()!=0):
        #média das diferenças
        dif=listKnowing[:, 1:]-listKnowing[:, :-1]
        dp=np.std(dif, ddof=0, axis=1).astype(int)
        value=np.max(dp)
        l=np.mean(dif, axis=1).astype(int)
        #print(l)
        if (value>(np.min(l))/6):
            listKnowing[np.argmax(dp)][-1]=0
            #desvio padrão reinicia tabela
            #print(dp)
            return -1
        nextTrans=l+listKnowing[:,-1]
        #print("next transmition "+str(nextTrans))
        l2=nextTrans-now+DeltaDelay#+np.random.randint(0,DeltaDelay*5,size=len(l))
        #print(l2)
        value=np.min(l2)
            
        #value=np.min(l2)
        #if(value<DeltaDelay and value>-(Nodes*DeltaDelay)):
        if(value<4*DeltaDelay):
            if(lastPoll==np.argmin(l2) and len(l2)>1):
                l3=l2
                l3[np.argmin(l2)]=1000
                value=np.min(l3)
                if(value<5*DeltaDelay):
                    return np.argmin(l3)
                else:
                    return -1
            else:
            #print(np.argmin(l2))
                return np.argmin(l2)
        else:
            return -1
    elif(modo=="knowing" and listKnowing.min()!=0):
        #média das diferenças
        l=np.mean(listKnowing[:, 1:]-listKnowing[:, :-1],axis=1).astype(int)
        #print(l)
        nextTrans=l+listKnowing[:,-1]
        #print("next transmition "+str(nextTrans))
        l2=nextTrans-now#+np.random.randint(0,DeltaDelay*5,size=len(l))
        #print(l2)
        value=np.min(l2)
        #if(value<DeltaDelay and value>-(Nodes*DeltaDelay)):
        if(value<(2*DeltaDelay)):
            #print(np.argmin(l2))
            return np.argmin(l2)
        else:
            return -1
    elif(modo=="FIFO"):
        AuxNode+=1
        AuxNode%=Nodes
        return AuxNode
    elif(modo=="random"):
        return np.random.randint(0,Nodes)
    else:
        AuxNode+=1
        AuxNode%=Nodes
        #print("p", end=' ')
        return AuxNode
        
    
def server(now):
    global PacketsSend
    global listDelay
    global listKnowing
    global packets
    global TPolls
    global lastPoll
    global lastlastPoll
    if (now%ServerInterval==0 or AuxNode==-1):
        nodePoll=Polling(DisciplinaServico,now)
        if(nodePoll!=-1):
            lastlastPoll=lastPoll
            lastPoll=nodePoll
            TPolls+=1
            #print("poll para "+ str(nodePoll)+" "+str(now))
            if(packets[nodePoll]!=0):
                if(np.random.randint(0,100)<SucessoTransmissao):
                    listDelay.append(now-packets[nodePoll])
                    listKnowing[nodePoll]=np.roll(listKnowing[nodePoll],-1)
                    listKnowing[nodePoll][qtdeAmostras-1]=now
                    PacketsSend+=1
                    #print(listKnowing)
                    packets[nodePoll]=0
            else:
                global lostPolls
                lostPolls+=1

def customer(now):
    global PacketsProduced
    global lostMsgs
    global packets
    global IntervalosAcumul
    listNow=(IntervalosAcumul*(-1))+now
    Htime=np.max(listNow)
    if (Htime>=0):
        i=np.argmax(listNow)
        if (packets[i]>0):
            lostMsgs+=1
            #print("perdeu ",i,packets[i])
        if (packets[i]==0):
            packets[i]=now
        IntervalosAcumul[i]+=Intervalos[i]
        PacketsProduced+=1
        #print(packets)

def main(first, end, passo,InterMin, InterMed, InterMax):
    
    global timeNow
    global ProcessingTime
    global listDelay
    global lostPolls
    global lostMsgs
    global listMedianDelay
    global Nodes
    global ProcessingTime #segundos
    global Intervalos 
    global IntervalosAcumul 
    global DistribuicaoIntervalos # aleatorio, poisson, exponential
    global packets
    global listLostMsgs
    global listSuccessPolls
    global listKnowing
    global listPollsWithoutResponse
    global listTotalPolls
    global listPacketsSend
    global listPacketsProduced
    global PacketsSend
    global PacketsProduced
    global listTPolls
    global TPolls
    
    ###quantidade de nós para cada simulação
    #first=10
    #end=30
    #passo=10
    for i in range (first,end+1,passo):
        PacketsProduced=0
        PacketsSend=0
        TPolls=0
        listDelay=[]
        lostPolls=0
        lostMsgs=0
        
        Nodes=i
        Intervalos = np.zeros(Nodes)
        IntervalosAcumul = np.zeros(Nodes)
        listKnowing.resize(Nodes,qtdeAmostras)

        if (DistribuicaoIntervalos=="linear"):
            Intervalos = np.random.randint(InterMin, InterMax, size=Nodes)
        elif(DistribuicaoIntervalos=="poisson"):
            Intervalos=np.random.poisson(InterMed, Nodes).astype(int)
            IntervalosAcumul=Intervalos.copy()
        elif(DistribuicaoIntervalos=="exponential"):
            Intervalos=np.random.exponential(InterMed, Nodes).astype(int)
            IntervalosAcumul=Intervalos.copy()
        elif(DistribuicaoIntervalos=="normal"):
            Intervalos=np.random.normal(InterMed, InterMed/3, Nodes).astype(int)
            IntervalosAcumul=Intervalos.copy()
        
        packets = np.zeros(Nodes)
        print (Intervalos)
    
        print("Simulating "+str(Nodes)+" Nodes "+str(ProcessingTime/1000)+" seconds "+DisciplinaServico)
        
        for timeNow in range(ProcessingTime):
            customer(timeNow)
            server(timeNow)

        listMedianDelay.append(statistics.median(listDelay))
        #print(listDelay)
        print("packets send: "+str(len(listDelay)))
        print("median delay: "+str(statistics.median(listDelay)))
        print("polls without response: "+str(lostPolls))
        print("success polls: "+str((len(listDelay)/(len(listDelay)+lostPolls))*100)+"%")
        print("lost msgs: "+str(lostMsgs)+" "+str(lostMsgs*100/len(listDelay))+"%" )
        listLostMsgs.append(lostMsgs*100/len(listDelay))
        listSuccessPolls.append(len(listDelay))
        listPollsWithoutResponse.append(lostPolls)
        listTotalPolls.append(len(listDelay)+lostPolls)
        listPacketsSend.append(PacketsSend)
        listPacketsProduced.append(PacketsProduced)
        listTPolls.append(TPolls)
        #print(listMedianDelay)
        #print(listKnowing)
    
    print("Median Delay", (listMedianDelay))
    plt.figure()
    plt.plot(listMedianDelay)
    plt.xlabel("mean delay")
    
    print("Lost msgs", (listLostMsgs))
    plt.figure()
    plt.plot(listLostMsgs)
    plt.xlabel("Lost msgs")
    
    print("Success polls", (listSuccessPolls))
    plt.figure()
    plt.plot(listSuccessPolls)
    plt.xlabel("Success Polls")
    
    print("Failed polls", (listPollsWithoutResponse))
    plt.figure()
    plt.plot(listPollsWithoutResponse)
    plt.xlabel("Failed Polls")
    
    print("Total Polls", (listTotalPolls))
    plt.figure()
    plt.plot(listTotalPolls)
    plt.xlabel("Total Polls")

    #arquivo csv
    # Open File
    now = datetime.datetime.now()
    datastr= ('{:02d}'.format(now.year)+'{:02d}'.format(now.month)+'{:02d}'.format(now.day)+"-"+'{:02d}'.format(now.hour)+'{:02d}'.format(now.minute)+'{:02d}'.format(now.second))
    resultFile = open((datastr+".csv"),'w', newline='')
    
    # Create Writer Object
    #wr = csv.writer(resultFyle, dialect='excel',delimiter=';')
    wr = csv.writer(resultFile, dialect='excel',delimiter=';')
    wr.writerow(["Disciplina",DisciplinaServico])
    wr.writerow(["Intervalos","Min","Med","Max"])
    wr.writerow([DistribuicaoIntervalos,InterMin,InterMed,InterMax])
    wr.writerow(["Tempo para cada amostra (seg)",(ProcessingTime/1000)])
    laux=["nodes","delay","lost msgs","success polls","failed polls","total polls","Packets Produced","Packets Send","Tpolls"]
    
    print("nodes\tdelay\tlost msgs\tsuccess polls\tfailed polls\ttotal polls")
    print(laux)
    wr.writerow(laux)
    
    j=0
    for i in range(first, end+1, passo):
        #print(i,j)
        laux=[]
        laux.append(str(i))
        laux.append(str(listMedianDelay[j]).replace('.',',').replace('[','').replace(']',''))
        laux.append(str(listLostMsgs[j]).replace('.',','))
        laux.append(str(listSuccessPolls[j]).replace('.',','))
        laux.append(str(listPollsWithoutResponse[j]).replace('.',','))
        laux.append(str(listTotalPolls[j]).replace('.',','))
        laux.append(str(listPacketsProduced[j]).replace('.',','))
        laux.append(str(listPacketsSend[j]).replace('.',','))
        laux.append(str(listTPolls[j]).replace('.',','))
        j+=1
        print(laux)
        wr.writerow(laux)    
        pass
    resultFile.close()
        
if (__name__=="__main__"):
    main(NodesBegin, NodesEnd, passo, InterMin, InterMed, InterMax)    
    