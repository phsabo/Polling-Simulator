# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 16:19:40 2018

@author: PauloHenrique
"""

import numpy as np
#import statistics
import matplotlib.pyplot as plt
import time
import csv
import argparse

print('\033[1m'+"Polling Simulator")
print("***use -h, --help")

#numero inicial, final de Nós
NodesBegin=1  
NodesEnd=1001
passo=50



#Intevalos de transmissão de cada nó e qual o tipo de distribuição
#InterMed utilizados nas distribuições poisson, exponential, normal e fixed 1/lambda
InterMed=1000    #miliseconds

#InterMax e InterMin utilizados somente quando a distribuição é uniforme
InterMin=32000    #miliseconds

InterMax=256000   #miliseconds
DistribuicaoIntervalos="uniforme2"# uniforme, poisson, exponential, normal, fixed, aleatoria

tipomudanca = -1# aleatório ou numero intevalo das mudanças em milisegundos inserir valor menor que 0 para não haver mudanças
qtdemudanca = 0.1 #porcentagem dos nós que irão alterar o seu intervao

#tempo de Processamento para cada conjunto de nós
ProcessingTime = 1000.0 #minutos
Probabilidade_de_erro=0#10**-3

#Taxa de sucesso na transmissão dos pacotes
SucessoTransmissao=1-Probabilidade_de_erro # Probabilidade de sucesso

#Tipo de disciplina utilizada na passagem dos polls 
RegraAtendimento = "predictstd" #Ciclico, predict, predictstd, random

#valor máximo de desvio padrão para atualização da tabela  quando utilizado RegraAtendimento = "predictstd"
CorrecaoSTD="250*np.log2(listMediaIntervalos/1000)+200"
#CorrecaoSTD="(listMediaIntervalos/InterMed)*1400"
maxSTD=1600
minSTD=100
#CorrecaoSTD="min(250*np.log2(listMediaIntervalos/1000)+200, (listMediaIntervalos/InterMed)*1600)"

#parâmetros da rede e dos nós
velocidadeTransmissao = 250000     #250000= 250kbps
#velocidadeTransmissao = 1000000    #1000000= 1Mbps
#velocidadeTransmissao = 2000000     #2000000= 2Mbps
tamanhoPacote = 32 #bytes 1 preamble, 5 pipe, 32 payload, 2 CRC
tamanhoControl = 3 #bytes 1 preamble, 5 pipe, 32 payload, 2 CRC
overhead = 9#
StartFromStandBy = 0.000130 #130us tempo modulo mudar rx->tx ou tx->rx
velocidadeSPI=400000 #400kbps
timeprocessing=0.7 # % coeficiente de tempo de processamento no calculo dos tempo s de acesso 



ap = argparse.ArgumentParser()
ap.add_argument("-b", "--begin", required=False, help="grupo de nós inicial")
ap.add_argument("-e", "--end", required=False, help="grupo de nós final")
ap.add_argument("-s", "--step", required=False, help="passo de nós entre cada simulação")
ap.add_argument("-i", "--intervalo", required=False, help="intevalo entre cada geração de pacotes por nó em mseg")
ap.add_argument("-t", "--time", required=False, help="tempo de simulação para cada grupo em min")
ap.add_argument("-r", "--rule", required=False, help="regra de atendimento (Ciclico, predict, predictstd, random)")
ap.add_argument("-v", "--velocidade", required=False, help="Datarate nominal (250000, 1000000, 2000000)")

ap.add_argument("-d", "--Distribuicao", required=False, help="uniforme, poisson, exponential, normal, fixed")
ap.add_argument("-imax", "--InterMax", required=False, help="InterMax e InterMin utilizados somente quando a distribuição é uniforme")
ap.add_argument("-imin", "--InterMin", required=False, help="InterMax e InterMin utilizados somente quando a distribuição é uniforme")

ap.add_argument("-S", "--sucesso", required=False, help="Taxa de sucesso na transmissão dos pacotes de 0-1 (padrão 0.9)")

ap.add_argument("-p", "--packet", required=False, help="tamanho do payload do pacote de dados (padrão 32)")
ap.add_argument("-c", "--control", required=False, help="tamanho do payload do pacote de controle (padrão 3)")
ap.add_argument("-o", "--overhead", required=False, help="tamanho do overhead por pacote (padrão 9)")
ap.add_argument("-ssb", "--startfromstandby", required=False, help="tempo para o modulo de rádio entrar nos modos RX ou TX (0.000130)")
ap.add_argument("-spi", "--SPIdatarate", required=False, help="velocidade de comunicação entre o microcontrolador e o módulo de rádio em  bps (padrão 400000)")
ap.add_argument("-E", "--timeprocessing", required=False, help="coeficiente de tempo de processamento nos tempos de comunicação (padrão 0.7)")

args = vars(ap.parse_args())
#print (args)
#print (args["InterMax"])




if(args["begin"]!=None):
    NodesBegin=int(args["begin"])
if(args["end"]!=None):
    NodesEnd=int(args["end"])
if(args["step"]!=None):
    passo=int(args["step"])
if(args["intervalo"]!=None):
    InterMed=int(args["intervalo"])
if(args["InterMax"]!=None):
    InterMax=int(args["InterMax"])
if(args["InterMin"]!=None):
    InterMin=int(args["InterMin"])
if(args["Distribuicao"]!=None):
    DistribuicaoIntervalos=(args["Distribuicao"])
if(args["time"]!=None):
    ProcessingTime=float(args["time"])
if(args["sucesso"]!=None):
    SucessoTransmissao=float(args["sucesso"])
if(args["rule"]!=None):
    RegraAtendimento=(args["rule"])
if(args["velocidade"]!=None):
    velocidadeTransmissao=int(args["velocidade"])
if(args["packet"]!=None):
    tamanhoPacote=int(args["packet"])
if(args["control"]!=None):
    tamanhoControl=int(args["control"])
if(args["overhead"]!=None):
    overhead=int(args["overhead"])
if(args["startfromstandby"]!=None):
    StartFromStandBy=float(args["startfromstandby"])
if(args["SPIdatarate"]!=None):
    velocidadeSPI=int(args["SPIdatarate"])
if(args["timeprocessing"]!=None):
    timeprocessing=float(args["timeprocessing"])



#calculo do tempo de serviço para os parâmetros anteriores
ProcessingTime *= 60000 #para milisegundos

airTime=(8*(overhead+tamanhoPacote))/velocidadeTransmissao   #tempo do pacote no ar
airTimeControl=(8*(overhead+tamanhoControl))/velocidadeTransmissao   #tempo do pacote no ar
timeUploadNodesControl=(8*tamanhoControl)/velocidadeSPI             #Tempo de recepção e envio via conexão SPI
timeUploadServerControl=(8*tamanhoControl)/velocidadeSPI
timeUploadNodes=(8*tamanhoPacote)/velocidadeSPI             #Tempo de recepção e envio via conexão SPI
timeUploadServer=(8*tamanhoPacote)/velocidadeSPI

#print("airTime: ",airTime)
#print("airTimeControl: ",airTimeControl)
#print("timeUploadNodesControl: ",timeUploadNodesControl)
#print("timeUploadServerControl: ",timeUploadServerControl)
#print("timeUploadNodes: ",timeUploadNodes)
#print("timeUploadServer: ",timeUploadServer)
#print(0.002500-timeUploadServerControl)
#totalTime=airTime*2+timeUploadNodes*2+timeUploadServer*2    #Server gera o poll           timeUploadServer
totalTime=0
totalTime+=StartFromStandBy+timeUploadServerControl+airTimeControl+timeUploadNodesControl 
                                                            #Server gera o poll           timeUploadServer
                                                            #Server envia o poll        + airTime
                                                            #Node recebe o poll         + timeUploadNodes
totalTime+=StartFromStandBy+timeUploadNodes+airTime+StartFromStandBy
                                                            #Node gera o pacote         + timeUploadNodes
                                                            #Node envia o pacote        + airTime
                                                            #Server recebe o pacote     + timeUploadServer
totalTime+=StartFromStandBy+timeUploadServerControl+airTimeControl+timeUploadNodesControl
                                                            #Server gera o ack           timeUploadServer
                                                            #Server envia o ack        + airTime
                                                            #Node recebe o ack         + timeUploadNodes

totalTimeWaitingPoll=StartFromStandBy+timeUploadServerControl+airTimeControl+timeUploadNodesControl+StartFromStandBy+timeUploadNodes+airTimeControl+timeUploadServerControl

                                                            #Server gera o poll           timeUploadServer
                                                            #Server envia o poll        + airTime
                                                            #Node recebe o poll         + timeUploadNodes
                                                            #Node gera o pacote         + timeUploadNodes
                                                            #Node envia o pacote        + airTime
                                                            #Server recebe pelo menos 1 byte     + timeUploadServerControl
                                                            #TotalTime em segundos      = totalTime
#print(totalTime)
tempoOcioso=(airTimeControl+timeUploadNodesControl)*1000*(1+timeprocessing)
TimeAccessQueueandServer=(totalTime*1000)*(1+timeprocessing)
#print("Access queue + Serviço: ",TimeAccessQueueandServer)
#print(totalTimeWaitingPoll)
TimeAccessQueue=(totalTimeWaitingPoll*1000)*(1+timeprocessing)
print("Tempo ocioso aguardando poll: ",tempoOcioso)
print("time Access Queue: ",TimeAccessQueue)
TimeService=TimeAccessQueueandServer-TimeAccessQueue
ServerInterval = TimeAccessQueueandServer  
print("time Service: ",TimeService)
print("limiar STD", CorrecaoSTD)
DeltaDelay=2*ServerInterval #intervalo de antecipação do envio dos polls
if ((ProcessingTime/60000)<(InterMed/120)):
    print("ATENÇÂO tempo de processamento mínimo sugerido = ", int(InterMed/120), " minutos por grupo")

#variaveis globais
Nodes=1
AuxPoll=0
Intervalos = np.zeros(Nodes)
IntervalosAcumul = np.zeros(Nodes)
listDelay=[]
lostPolls=0
lostMsgs=0
listMeanDelay=[]
listLostMsgs=[]
listSuccessPolls=[]


####################
qtdeAmostras=5 #largura da tabela, quantidade de amostras de tempo utilizadas na predição
listTimes=np.zeros(1) ###lista dos instantes dos ultimos pacotes recebidos
####################

listNodestoSend=np.zeros(1)
listTotalPolls=[]
listPollsWithoutResponse=[]
listPacketsProduced=[]
PacketsProduced=0
listPacketsSend=[]
PacketsSend=0
listTPolls=[]
TPolls=0

lastPoll=0

#np.random.seed(59)
 
#variáveis da predição   
listIntervalos=0  #intervalos entre transmissões
listSTDnodes=0 #desvio padrão dos intervalos
listMediaIntervalos=0 #média de tempo entre cada transmissão
lstdvalues=0 

listTimesSimul=[]

def printHour(date, endchar):
    hora=time.localtime(date)
    print('{:02d}'.format(hora.tm_year)+'{:02d}'.format(hora.tm_mon)+'{:02d}'.format(hora.tm_mday)+"-"+'{:02d}'.format(hora.tm_hour)+":"+'{:02d}'.format(hora.tm_min)+":"+'{:02d}'.format(hora.tm_sec), end=endchar)

def printHourPassed(date, endchar):
    segundos=(date%60)
    date=(date-segundos)/60
    segundos=int(segundos)
    minutos =int((date)%60)
    date=(date-minutos)/60
    hora = int(date%24)
    date=(date-hora)/24
    dias = int(date)
    print('{:02d}'.format(dias)+"-"+'{:02d}'.format(hora)+":"+'{:02d}'.format(minutos)+":"+'{:02d}'.format(segundos), end=endchar)




packets = np.zeros(Nodes)

print("Simulating")
#nowinit = datetime.datetime.now()
#print('{:02d}'.format(nowinit.hour)+":"+'{:02d}'.format(nowinit.minute)+":"+'{:02d}'.format(nowinit.second))
nowinit = time.time()
printHour(nowinit, "\n")
aux=0


print("Group Ndes begn\t\t", NodesBegin)
print("Group Ndes end\t\t", NodesEnd)
print("Nodes step\t\t", passo)
print("Nodes intervalo\t\t", InterMed , "mseg")
print("time simulation\t\t", ProcessingTime/60000, "minutos por grupo" )
print("Regra de atendimento\t", RegraAtendimento )
print("AirDataRate\t\t", velocidadeTransmissao/1000, "kbps" )



#Atualiza a predição após cada pacote recebido
def attPredict(modo):
    global listIntervalos
    global listSTDnodes
    global listMediaIntervalos
    global lstdvalues
    global listTimes
    listIntervalos=listTimes[:, 1:]-listTimes[:, :-1]
    listSTDnodes=np.std(listIntervalos, ddof=0, axis=1).astype(int)
    listMediaIntervalos=np.mean(listIntervalos, axis=1).astype(int)
    #CorrecaoSTD="250*np.log2(listMediaIntervalos/1000)+200"
    #lstdvalues= 250*np.log2(listMediaIntervalos/1000)+200 #CorrecaoSTD
    if(modo=="predictstd"):
        lstdvalues= eval(CorrecaoSTD) #CorrecaoSTD
        
        lstdvalues[lstdvalues>maxSTD]=maxSTD
        lstdvalues[lstdvalues<minSTD]=minSTD
        
        if (np.min(lstdvalues-listSTDnodes)<0):
            listTimes[np.argmin(lstdvalues-listSTDnodes)][-1]=0 #correção std
    

def Polling(modo,now):
    global AuxPoll
    global aux
    global lastPoll

    global listNodestoSend
    #if (now%360000==0):#forca atualização da tabela a cada 2mim, 1min=60000ms
    if (now%(60*InterMed)==0):#forca atualização da tabela 
        #listTimes[-1][-1]=0
        pass
    if(modo=="predictstd" and listTimes.min()!=0): #predição com correção de desvio padrão se a lista estiver preenchida
        nextTrans=listMediaIntervalos+listTimes[:,-1]
        countdown=nextTrans-now
        value=np.min(countdown)
        if(value<2*DeltaDelay):
            for i in range(len(countdown)):
                if (countdown[i]<2*DeltaDelay):
                    listNodestoSend[i]=1
                else:
                    listNodestoSend[i]=0
            for i in range(lastPoll+1,lastPoll+1+len(listNodestoSend)):
                if listNodestoSend[i%len(listNodestoSend)]==1:
                    return i%len(listNodestoSend)
        else:
            return -1
    elif(modo=="predict" and listTimes.min()!=0): #predição sem correções
        nextTrans=listMediaIntervalos+listTimes[:,-1]
        countdown=nextTrans-now
        #print(countdown)
        value=np.min(countdown)
        if(value<2*DeltaDelay):
            for i in range(len(countdown)):
                if (countdown[i]<2*DeltaDelay):
                    listNodestoSend[i]=1
                else:
                    listNodestoSend[i]=0
                    
            for i in range(lastPoll+1,lastPoll+1+len(listNodestoSend)):
                if listNodestoSend[i%len(listNodestoSend)]==1:
                    return i%len(listNodestoSend)
        else:
            return -1
    elif(modo=="Ciclico"): #
        AuxPoll+=1
        AuxPoll%=Nodes
        return AuxPoll
    elif(modo=="random"):
        return np.random.randint(0,Nodes)
    else:
        AuxPoll+=1
        AuxPoll%=Nodes
        return AuxPoll

def mudaintervalos(Intervalos, now):
    global Nodes
    global tipomudanca
    global qtdemudanca
    
    if (tipomudanca=="aleatorio"):
        if(np.random.randint(0,100) < 5):
            print("mudou")
            qtde=int(Nodes*qtdemudanca)
            for i in range(qtde):
                Intervalos[i]+=np.random.randint(int(-InterMed/2),int(InterMed/2)) 
    elif (tipomudanca>0):
        if (now >0 and now%tipomudanca<1):
            print("mudou")
            qtde=int(Nodes*qtdemudanca)
            for i in range(qtde):
                Intervalos[i]+=np.random.randint(int(-InterMed/2),int(InterMed/2)) 

    return Intervalos
        
#consome os pacotes    
def server(now):
    global PacketsSend
    global listDelay
    global listTimes
    global packets
    global TPolls
    global lastPoll
    global AuxPoll
    global timeNow
        
    nodePoll=Polling(RegraAtendimento,now)
    AuxPoll=nodePoll
    if(nodePoll!=-1):
        lastPoll=nodePoll
        TPolls+=1
        #print("poll para "+ str(nodePoll)+" "+str(now))
        if(packets[nodePoll]!=0):
            if(np.absolute(np.random.random())<SucessoTransmissao):
                timeNow+=(TimeAccessQueue + TimeService)
                #print("a")
                listDelay.append(now-packets[nodePoll])
                listTimes[nodePoll]=np.roll(listTimes[nodePoll],-1)
                listTimes[nodePoll][qtdeAmostras-1]=now
                PacketsSend+=1
                packets[nodePoll]=0
                if (listTimes.min()!=0):
                    attPredict(RegraAtendimento) #atualiza a predição
            else:
                timeNow+=(TimeAccessQueue + TimeService)
                #print("b")
        else:
            global lostPolls
            lostPolls+=1
            timeNow+=TimeAccessQueue
                
    else:
        timeNow+=1#tempo process new poll
def distrUniforme(Mi, Ma, N):
    distr=[]
    if (N!=1):        
        passo=int((Ma-Mi)/(N-1))
    else:
        passo=int((Ma-Mi)/(N))
    for i in range (N):
        distr.append(Mi+(passo*i))
    return distr


#produz os pacotes 
def customer(now):
    global PacketsProduced
    global lostMsgs
    global packets
    global IntervalosAcumul
    global Intervalos
    
    listNow=(IntervalosAcumul*(-1))+now
    Htime=np.max(listNow)
    if (Htime>=0):
        for i in range(len(listNow)):
            if listNow[i]>=0:
        
                if (packets[i]>0):
                    lostMsgs+=1
                    #print("perdeu ",i,packets[i])
                if (packets[i]==0):
                    packets[i]=now
                IntervalosAcumul[i]+=Intervalos[i]
                PacketsProduced+=1
                #print(packets)
    mudaintervalos(Intervalos, now)

def main(first, end, passo,InterMin, InterMed, InterMax):
    
    global timeNow
    global ProcessingTime
    global listDelay
    global lostPolls
    global lostMsgs
    global listMeanDelay
    global Nodes
    global ProcessingTime #segundos
    global Intervalos 
    global IntervalosAcumul 
    global DistribuicaoIntervalos # aleatorio, poisson, exponential
    global packets
    global listLostMsgs
    global listSuccessPolls
    global listTimes
    global listNodestoSend
    global listPollsWithoutResponse
    global listTotalPolls
    global listPacketsSend
    global listPacketsProduced
    global PacketsSend
    global PacketsProduced
    global listTPolls
    global TPolls
    global listTimesSimul
    nowTime = time.time()
    for i in range (first,end+1,passo):
        np.random.seed(np.random.randint(1,1000))
        PacketsProduced=0
        PacketsSend=0
        TPolls=0
        listDelay=[]
        lostPolls=0
        lostMsgs=0
        
        Nodes=i
        Intervalos = np.zeros(Nodes)
        IntervalosAcumul = np.zeros(Nodes)
        listTimes.resize(Nodes,qtdeAmostras)
        listNodestoSend.resize(Nodes,1)
        
        if (DistribuicaoIntervalos=="uniforme"):
            Intervalos = np.random.uniform(InterMin, InterMax+1, size=Nodes)
            #print(np.mean(Intervalos))
            #print(np.amin(Intervalos))
            #print(np.amax(Intervalos))
            #IntervalosAcumul=Intervalos.copy()
        elif (DistribuicaoIntervalos=="uniforme2"):
            Intervalos = np.array(distrUniforme(InterMin, InterMax, Nodes))
            #print((Intervalos))
            #print(np.amin(Intervalos))
            #print(np.amax(Intervalos))
            #IntervalosAcumul=Intervalos.copy()
        elif(DistribuicaoIntervalos=="aleatoria"):
            Intervalos = np.random.randint(InterMin, InterMax+1, size=Nodes)
            #IntervalosAcumul=Intervalos.copy()
        elif(DistribuicaoIntervalos=="poisson"):
            Intervalos=np.random.poisson(InterMed, Nodes).astype(int)
            #IntervalosAcumul=Intervalos.copy()
        elif(DistribuicaoIntervalos=="exponential"):
            Intervalos=np.random.exponential(InterMed, Nodes).astype(int)
            #IntervalosAcumul=Intervalos.copy()
        elif(DistribuicaoIntervalos=="normal"):
            Intervalos=np.random.normal(InterMed, InterMed/3, Nodes).astype(int)
            #IntervalosAcumul=Intervalos.copy()
        elif(DistribuicaoIntervalos=="fixed"):
            Intervalos=(np.zeros(Nodes).astype(int)+InterMed)
            #IntervalosAcumul=Intervalos.copy()
        IntervalosAcumul+=(np.random.randint(0,InterMax,Nodes))
        #IntervalosAcumul+=(np.arange(0,Nodes)*10)
        packets = np.zeros(Nodes)
        
        ##printar intervalos
        #print (Intervalos)
    
        print("--  Simul "+str(Nodes)+" Nodes \t\t|"+str(ProcessingTime/1000)+" segs \t|"+RegraAtendimento+" \t| tempo de sim. ", end="")
        printHourPassed(sum(listTimesSimul), "\n")
        timeNow=0
        while timeNow <= ProcessingTime:
            customer(timeNow)
            server(timeNow)
#            precision

        listMeanDelay.append(np.mean(listDelay))
        print("mean Delay: %.3f ms" % ((np.mean(listDelay))), end="\t\t")
        print("| success polls: %.2f%%" % (((len(listDelay)/(len(listDelay)+lostPolls))*100)), end="\t\t")
        print("| packets send: "+str(len(listDelay)))
        print("lost msgs: "+str(lostMsgs)+" %.2f%% " % (lostMsgs*100/len(listDelay)), end="\t\t| tempo ")
        listLostMsgs.append(lostMsgs*100/len(listDelay))
        listSuccessPolls.append(len(listDelay))
        listPollsWithoutResponse.append(lostPolls)
        listTotalPolls.append(len(listDelay)+lostPolls)
        listPacketsSend.append(PacketsSend)
        listPacketsProduced.append(PacketsProduced)
        listTPolls.append(TPolls)
        listTimesSimul.append(time.time()-nowTime)
        nowTime=time.time()
        printHourPassed(listTimesSimul[-1], "")
        print("\t\t| fim em:", end="")
        
        if (len(listTimesSimul)>1):
            auxTime=[]
            for i in range(len(listTimesSimul)-1):
                auxTime.append(listTimesSimul[i+1]-listTimesSimul[i])
            r=np.mean(auxTime)
            if (r<0):
                r=0
            nexttime=listTimesSimul[-1] #valor de an
            nexttime+=(((end-first)/passo)-(len(listTimesSimul)))*r
            
            nexttime+=listTimesSimul[-1] #soma com a1
            nexttime*=((((end-first)/passo)+1-len(listTimesSimul))/2) #multiplica por n/2
            printHour(time.time()+nexttime, "")
        print()
        print("--------------------------------------------------------------------------------------")
        
    x=np.arange(NodesBegin,NodesEnd+1, passo)
    #print("Mean Delay", (listMeanDelay))
    plt.figure()
    plt.plot(x,listMeanDelay)
    plt.ylabel("mean delay")
    plt.xlabel("Nodes")
    
    #print("Lost msgs (%)", (listLostMsgs))
    plt.figure()
    plt.plot(x,listLostMsgs)
    plt.ylabel("Lost msgs (%)")
    plt.xlabel("Nodes")
    
    #print("Success polls", (listSuccessPolls))
    plt.figure()
    plt.plot(x,listSuccessPolls)
    plt.ylabel("Success Polls")
    plt.xlabel("Nodes")
    
    #print("Failed polls", (listPollsWithoutResponse))
    plt.figure()
    plt.plot(x,listPollsWithoutResponse)
    plt.ylabel("Failed Polls")
    plt.xlabel("Nodes")
    
    #print("Total Polls", (listTotalPolls))
    plt.figure()
    plt.plot(x,listTotalPolls)
    plt.ylabel("Total Polls")
    plt.xlabel("Nodes")
    
    #arquivo csv
    # Open File
    #now = datetime.datetime.now()
    #datastr= ('{:02d}'.format(now.year)+'{:02d}'.format(now.month)+'{:02d}'.format(now.day)+"-"+'{:02d}'.format(now.hour)+'{:02d}'.format(now.minute)+'{:02d}'.format(now.second))
    now = time.localtime(time.time())
    datastr= ('{:02d}'.format(now.tm_year)+'{:02d}'.format(now.tm_mon)+'{:02d}'.format(now.tm_mday)+"-"+'{:02d}'.format(now.tm_hour)+'{:02d}'.format(now.tm_min)+'{:02d}'.format(now.tm_sec))
    print(datastr)
    resultFile = open((datastr+".csv"),'w', newline='')
    
    TempoSimulacao=time.time()-nowinit
    print("Qtde de simulações= ", end="")
    print((NodesEnd-NodesBegin)/passo)
    print("Tempo de simulação= ", end="")
    printHourPassed(TempoSimulacao, "\n")
    
    
    # Create Writer Object
    wr = csv.writer(resultFile, dialect='excel',delimiter=';')
    wr.writerow(["Disciplina",RegraAtendimento, "correção STD", CorrecaoSTD, "Sucesso transmissão", SucessoTransmissao])
    wr.writerow(["Largura de banda bps",velocidadeTransmissao, "tempo serviço (s)", str(TimeService/1000).replace('.',','), "tempo fila", str(TimeAccessQueue/1000).replace('.',',') ])
    wr.writerow(["Intervalos (s)","Min","Med","Max"])
    wr.writerow([DistribuicaoIntervalos,InterMin,InterMed,InterMax])
    wr.writerow(["Tempo para cada amostra (s)",str(ProcessingTime/1000).replace('.',','),"","Probabilidade de erro",Probabilidade_de_erro])
    laux=["nodes","delay (ms)","% lost msgs","success polls","failed polls","total polls","Packets Produced","Packets Send","Tpolls"]
    
    print(laux)
    wr.writerow(laux)
    
    j=0
    for i in range(first, end+1, passo):#substituir ponto por vírgula pra operações em app de planilha eletronica
        #print(i,j)
        laux=[]
        laux.append(str(i))
        laux.append(str(listMeanDelay[j]).replace('.',',').replace('[','').replace(']',''))
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
    