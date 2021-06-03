# coding: utf-8
from pymodbus.server.asynchronous  import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from twisted.internet.task import LoopingCall
from pymodbus.pdu import ModbusRequest
import serial
import time
import datetime
from datetime import timedelta
from datetime import date
from datetime import datetime
import threading
import string
import os
import glob

import Adafruit_BMP.BMP085 as BMP085
import struct
import smbus
import RPi.GPIO as GPIO
import tkinter
import tkinter as tk
from tkinter import *
from tkinter import ttk
mainWin = Tk()
mainWin.title('TIC & Temp')

"*******************gpio**********************"
GPIO.setmode(GPIO.BOARD)
""" ignore les msg d'alarme """
GPIO.setwarnings(False)
"""affectation des pin gpio Custard pi 2"""
"""entree"""

#GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#entree analogique
GPIO.setup(21, GPIO.IN)

"""sorties """
GPIO.setup(11, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)
#pour lecture analogique
GPIO.setup(24, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
#init
GPIO.output(24,True)
GPIO.output(23,False)
GPIO.output(19,True)
out1=0
out2=0
out3=0
out4=0
out5=0
out6=0
out7=0
out8=0
out=[0,0,0,0,0,0,0,0]
init=0
######################### LOAD PARAMS at startup ###############################
def load():
    global init
    pr=[0,0,0,0]
    on=[0,0,0,0]
    debut=[0,0,0,0,0]
    fin=[0,0,0,0,0]
    days=[0, 0, 0, 0, 0]
    alldays=[]  
    fichier = "/home/pi/paramsPisc.csv"
    f=open(fichier,"r")
    ligne=f.readlines()
    
    for index in range (0,4):
        pr[index]=ligne[index]
        #print(pr)
        on[index]= (pr[index][5:8])
        debut[index] =(pr[index][9:17])
        fin[index] =(pr[index][18:26])
        days[index]=(pr[index][28:47])
       
   
    #erase old values
    HOnPiscine.delete(0,END)
    HOnPiscine2.delete(0,END)
    
    
    HOffPiscine.delete(0,END)
    HOffPiscine2.delete(0,END)
    
   
    #load state of buttons#
    B1.config(text=on[0])
    B2.config(text=on[1])
    B3.config(text=on[2])
    B4.config(text=on[3])
    
    #load debut entrys#
    HOnPiscine.insert(0,debut[0])
    HOnPiscine2.insert(0,debut[1])
    
    
    #load fin entrys#
    HOffPiscine.insert(0,fin[0])
    HOffPiscine2.insert(0,fin[1])
    
    #load days checked
    #mise en forme
    n=0
    chek=[]
    for x in range(0,2):
        for z in range (0,len(days[x])):
         if days[x][z].isnumeric():              
            chek.append(int(days[x][z]))
            #print (chek)
        
    for n in range (0,len(chek)):   
        vars[n].set(chek[n])
    f.close()
    init=1
    print ('load')
    
######################### STORE PARAMS ################################
def store(*args):
    global init
    #print(init)
    
    global etat1,debut1,fin1,etat2,debut2,fin2,etat3,debut3,fin3,etat4,debut4,fin4,etat5,debut5,fin5,flag
    debut1=datetime.strptime(HOnPiscine.get(), "%H:%M:%S").strftime("%H:%M:%S")
    debut2=datetime.strptime(HOnPiscine2.get(), "%H:%M:%S").strftime("%H:%M:%S")
    
    fin1=datetime.strptime(HOffPiscine.get(), "%H:%M:%S").strftime("%H:%M:%S")
    fin2=datetime.strptime(HOffPiscine2.get(), "%H:%M:%S").strftime("%H:%M:%S")
    
    etat1=B1.config('text')[-1]
    etat2=B2.config('text')[-1]
    etat3=B3.config('text')[-1]
    etat4=B4.config('text')[-1]
    
    checked=[0,0,0,0,0,0,0,
            0,0,0,0,0,0,0]
                
    for x in range(0,14):
        checked[x]=vars[x].get()
    #print (checked)
    if init ==1:
        fichier = "/home/pi/paramsPisc.csv"
        f=open(fichier,"w")
        f.writelines ('prg1:'+str(etat1)+";"+str(debut1)+";"+str(fin1)+";"+str(checked[0:7])+"\n"+
                      'prg2:'+str(etat2)+";"+str(debut2)+";"+str(fin2)+";"+str(checked[7:14])+"\n"+
                      'robo:'+str(etat3)+"\n"+
                      'Chau:'+str(etat4)+"\n")
        
        
        f.close()
        print ('update')


"""partie analog custardpi"""
class analogcustard(threading.Thread):
    def __init__(self,nom = 'analogcustard'):
      threading.Thread.__init__(self)
      self.nom=nom
      self.terminated = False
      self.volt = 0
    def run(self):
        
                  print (' analogcustard')
                  while True:
                      GPIO.output(24,False)
                      anip=0  
                      word1=[1,1,0,1,1]
                      for x in range (0,5):
                            GPIO.output(19, word1[x])
                            time.sleep(0.01)
                            GPIO.output(23, True)
                            time.sleep(0.01)
                            GPIO.output(23, False)
                      for x in range (0,12):
                            GPIO.output(23,True)
                            time.sleep(0.01)
                            bit=GPIO.input(21)
                            time.sleep(0.01)
                            GPIO.output(23,False)
                            value=bit*2**(12-x-1)
                            anip=anip+value
                      GPIO.output(24,True)
                      volt=anip*3.3/4096
                      #print(volt)
                      self.volt=int(volt*100)
                      labelai63.config(text=str(volt))
                      pb4.config(value=volt)   
                          
    def stop(self):
              self._stopevent.set()
              
"""partie one wire ds18b20"""
class ds18b20(threading.Thread):
    def __init__(self,nom = 'ds18b20'):
      threading.Thread.__init__(self)
      self.nom=nom
      self.terminated = False
      self.temp_c = 0
    def run(self):
        
                
                  print ('thread one wire')
                  while True:
                        base_dir = '/sys/bus/w1/devices/'
                        if os.path.isdir((base_dir + '28-01191a013e9f')):
                            device_folder = glob.glob(base_dir + '28-01191a013e9f')[0]
                            device_file = device_folder + '/w1_slave'
                            if os.path.isfile(device_file):
                                f = open(device_file, 'r')
                                lines = f.readlines()
                                f.close()
                                time.sleep(1)
                                #print (lines)
                                if(lines[0].strip()[-3:] == 'YES') :#crc ok
                                    #print(lines[1].strip()[-5:])
                                    if 't=' in lines[1]:
                                       pos=(lines[1].index('=')) #cherche la position du =
                                       tempstr=(lines[1][pos+1:]) #prend ce qui suit le =
                                       self.temp_c =int(int(tempstr)/10) # str to int
                                       #print (self.temp_c) 
                                       #temp eau          
                                       labelai21.config(text=str((onewire.temp_c /100)))          
                                       pb2.config(value=(onewire.temp_c /100))
                                       time.sleep(2)
                            else:
                                print ('no ds18B20 2')
                                labelai21.config(text=str((-1)))          
                                pb2.config(value=(-1))
                                self.temp_c =-9999
                                time.sleep(2)
                        else:
                            print ('no ds18B20 1')
                            self.temp_c =-9999
                            labelai21.config(text=str((-1)))          
                            pb2.config(value=(-1))
                            time.sleep(2)
                            
                        
                  
        
              
    def stop(self):
              self._stopevent.set()

 

 
"""**********************partie i2c bmp085 *******************"""
class i2cbmp085(threading.Thread):
    def __init__(self,nom = 'i2cbmp085'):
      threading.Thread.__init__(self)
      self.nom=nom
      self.terminated = False
      self.temp=0
      
    def run(self):
                  print ('thread i2c bmp085')
                  sensor = BMP085.BMP085()
                  while True:
                    temperature=int((sensor.read_temperature())*10)
                    if temperature != '':
                        self.temp=temperature
                    else:
                        self.temp= 99
                        
                    #print(self.temp)
                    time.sleep(0.5)
                    #temp ext             
                    labelai20.config(text=str(bmp085.temp/10))           
                    pb1.config(value=(bmp085.temp/10))  
    def stop(self):
              self._stopevent.set()
"""**************************lecture du port serie************************"""    

    
"""**************************partie serie************************"""

class readFromSerial(threading.Thread):
     def __init__(self,nom='serial'):
         global  PA
         self.nom=nom
         self.terminated = False
         self.I1=0
         self.I2=0
         self.I3=0
         self.PA=0
         self.Index=0
         self.IndexF=0
         self.Indexf=0
         
         try:
                    threading.Thread.__init__(self)
                    self.setDaemon(True)
              
                    print ('serial init')
                    self._ser = serial.Serial(	port='/dev/ttyUSB0',
                                                    baudrate=1200, 
                                                    parity=serial.PARITY_EVEN,                                        
                                                    stopbits=serial.STOPBITS_ONE,                                         
                                                    bytesize=serial.SEVENBITS,                                        
                                                    timeout=1)                                        
                    print ('Serial initialized')
                    self._OK = 1
         except:
                    print ('usb tic error')
     def __del__(self):
        self._ser.close()
        
     def run(self):
            while True:
                    try:
                        trame = self._ser.readline()
                        #print (trame)
                        if b'IINST1 'in trame:
                             
                             if (trame[7:10].isdigit() == True):
                                    self.I1 = int(trame[7:10])
                                    #print (self.I1)
                        if b'IINST2 'in trame:
                            
                             if (trame[7:10].isdigit() == True):
                                     self.I2 = int(trame[7:10])
                                     #print (self.I2)
                        if b'IINST3 'in trame:
                            
                             if (trame[7:10].isdigit() == True):
                                     self.I3 = int(trame[7:10])
                                     #print (self.I3)
                        if b'PAPP 'in trame:
                            
                             if (trame[5:10].isdigit() == True):
                                     self.PA = int(trame[5:10])
                                     #print (self.PA)
                        if b'BASE 'in trame:
                            
                             if (trame[5:10].isdigit() == True):
                                     self.index = int(trame[5:14])
                                     #print (self.index)
                                    
                        #mot double index
                        binindex=bin(self.index) #en binaire
                        long=len (binindex)#nb de bits 0b10111011000110000
                        #print(long)
                        pf=binindex[(long-16):]#prend le nombre de bits - moins 16 bitspour le poids faible depuis le debut 0b1011000110000  
                        pF=binindex[:(long-16)]#prend le nombre de bits - moins 16 bitspour le poids fort depuis la fin 0b1011
                        pff= '0b' + pf #complemente avec 0b pour indiquer que c'est du binaire
                        #print (pF,pff)
                        self.IndexF=int(pF,2) #convert to int
                        self.Indexf=int(pff,2)#convert to int          
                        #print (self.IndexF,self.Indexf)

                        #conso           
                        labelai31.config(text=str((serial.PA)))          
                        pb3.config(value=serial.PA)                            
                    except:
                           # print ('Serial no data')
                            time.sleep(0.5)

                
"""**************************partie modbus avec pymodbus installé************************"""

class modbus(threading.Thread):
    def __init__(self,nom = 'modbus'):
      threading.Thread.__init__(self)
      self.nom=nom
      self.terminated = False
    
    def run(self): 
            print ('Thread modbus ')
            """**************declare le nb de mots ***********************"""
            store = ModbusSlaveContext(
                di = ModbusSequentialDataBlock(0, [0]*100),
                co = ModbusSequentialDataBlock(0, [0]*100),
                hr = ModbusSequentialDataBlock(0, [0]*100),
                ir = ModbusSequentialDataBlock(0, [0]*100))
            context = ModbusServerContext(slaves=store, single=True)

            """**************************ecrit les entrees dans le module modbus************************"""
            def signed(value):
                packval =struct.pack('<h',value)
                return struct.unpack('<H',packval)[0]
            
            def updating_writer(a):

                context  = a[0]
                register = 3
                slave_id = 0
                address  = 10 # mot w10 
                values = [serial.I1,serial.I2,serial.I3,serial.PA,serial.Indexf,serial.IndexF,custardanalog.volt,0,0,0,
                          signed(onewire.temp_c),GPIO.input(22),signed(bmp085.temp)]
                  
                context[slave_id].setValues(register,address,values)
            """*********lit les valeurs du module modbus et les ecrit sur les gpio************************"""
            def read_context(a):
                 global value
                 context  = a[0]
                 register = 3
                 slave_id = 0
                 address  = 30 # mot w30 
                 value = context[slave_id].getValues(register,address,10)


                 ######### local plc write value   ################
                 if  out1 == 1 :
                  value[3] = out1#pompe
                 if out2==1:
                  value[3] = out2#pompe
                 if out3==1:
                  value[2] = out3#robot
                 if out4==1:
                  value[1] = out4#chauff
                 if out5==1:
                  value[0] = out5#lampe
                  
                 """ ecriture des sorties mot w30 """
                 if value[0]==0:GPIO.output(11, GPIO.LOW)#w30 eclairage
                 if value[0]==1:GPIO.output(11, GPIO.HIGH)
                 if value[1]==0:GPIO.output(12, GPIO.LOW)#w31 chauff
                 if value[1]==1:GPIO.output(12, GPIO.HIGH)
     
                     
                 """print ((signed(bmp085.temp)),(signed(onewire.temp_c)))"""
                 if  signed(bmp085.temp)<-150 or signed(onewire.temp_c)<10:#hors gel
                     GPIO.output(13, GPIO.HIGH)
                     GPIO.output(15, GPIO.HIGH)
                 else:
                     if value[2]==0:GPIO.output(13, GPIO.LOW)#w32 robot
                     if value[2]==1:GPIO.output(13, GPIO.HIGH)
                     if value[3]==0:GPIO.output(15, GPIO.LOW)#w33 pompe
                     if value[3]==1:GPIO.output(15, GPIO.HIGH)
              
                 #print (value)
                 #affichage io
                 #input
                 labelai6.config(text=str((GPIO.input(11),GPIO.input(12),GPIO.input(13),GPIO.input(15))))
                 #output
                 labelai7.config(text=str((not GPIO.input(22),not GPIO.input(18),not GPIO.input(16))))
                  
                 

            read = LoopingCall(f=read_context, a=(context,))
            read.start(.2)

            write = LoopingCall(f=updating_writer, a=(context,))
            write.start(.2)
            StartTcpServer(context)
            
        
    def stop(self):
                 self._stopevent.set()

"""**************************partie threading************************"""
if __name__ == '__main__':
    
    #### PLC ####  
    def update_Out():
        now = time.strftime("%H:%M:%S")
        label10.configure(text=now)
        mainWin.after(1000, update_Out)
        
        global out1,out2,out3,out4,out5
        
        ######### jours   #######

        NumJour= datetime.today().weekday()
        checked=[0,0,0,0,0,0,0,
                 0,0,0,0,0,0,0,
                 ]
        
        for x in range(0,14):
            checked[x]=vars[x].get()

        if checked[NumJour]==1:
            daycheck1=True
        else:
            daycheck1=False
        if checked[NumJour+7]==1 :
            daycheck2=True
        else:
            daycheck2=False
        
        #piscine
        if B6.config('text')[-1]=='On 'or (B1.config('text')[-1]=='On 'and
                                          now >datetime.strptime(HOnPiscine.get(), "%H:%M:%S").strftime("%H:%M:%S") and
                                          now <datetime.strptime(HOffPiscine.get(), "%H:%M:%S").strftime("%H:%M:%S")and daycheck1==True ):
            out1=1
        else :
            out1=0
        #piscine2
        if B7.config('text')[-1]=='On 'or (B2.config('text')[-1]=='On 'and
                                          now >datetime.strptime(HOnPiscine2.get(), "%H:%M:%S").strftime("%H:%M:%S") and
                                          now <datetime.strptime(HOffPiscine2.get(), "%H:%M:%S").strftime("%H:%M:%S")and daycheck2==True ):
            out2=1
        else :
            out2=0 
        #robot   
        if (B3.config('text')[-1]=='On 'and ( out1 or out2))or B8.config('text')[-1]=='On ':
            out3=1
        else:
            out3=0
        #chauffage
        if (B4.config('text')[-1]=='On 'and (out1 or out2))or B9.config('text')[-1]=='On ':
            out4=1
        else:
            out4=0
         #Lampe
        if B5.config('text')[-1]=='On ':
            out5=1
        else:
            out5=0

 ########################### hmi   #####################################
                    
    #Label für Kanalbestimmung (unwichtig) column 16
    bai1 = ttk.Label(mainWin, width=13, text='Temp Ext: ')
    bai1.grid(row=1,column=16)
    bai2 = ttk.Label(mainWin, width=13, text='Temp Eau: ')
    bai2.grid(row=2,column=16)
    bai3 = ttk.Label(mainWin, width=13, text='Conso Watt: ')
    bai3.grid(row=3,column=16)
    bai6 = ttk.Label(mainWin, width=13, text='Analog: ')
    bai6.grid(row=4,column=16)

    #Labels column 17
    labelai20 = ttk.Label(mainWin, width=13)
    labelai20.grid(row=1,column=17)
    labelai21 = ttk.Label(mainWin, width=13)
    labelai21.grid(row=2,column=17)
    labelai31 = ttk.Label(mainWin, width=13)
    labelai31.grid(row=3,column=17)
    
    labelai63 = ttk.Label(mainWin, width=13)
    labelai63.grid(row=4,column=17)
    labelai6 = ttk.Label(mainWin, width=20)
    labelai6.grid(row=7,column=18)
    labelai7 = ttk.Label(mainWin, width=20)
    labelai7.grid(row=6,column=18)

    #Progressbar column 18
    pb1 = ttk.Progressbar(mainWin, orient='horizontal', maximum=50, length=100, mode='determinate')
    pb1.grid(row=1,column=18)
    pb2 = ttk.Progressbar(mainWin, orient='horizontal', maximum=50, length=100, mode='determinate')
    pb2.grid(row=2,column=18)
    pb3 = ttk.Progressbar(mainWin, orient='horizontal', maximum=5000, length=100, mode='determinate')
    pb3.grid(row=3,column=18)
    pb4 = ttk.Progressbar(mainWin, orient='horizontal', maximum=5, length=100, mode='determinate')
    pb4.grid(row=4,column=18)
        
    """buttons horo"""
    def OnPiscine():
        global etat1
        if  B1.config('text')[-1]=='Off':
            B1.config(text='On ')
            etat1=B1.config('text')[-1]
            store()
        else:
            B1.config(text='Off')
            etat1=B1.config('text')[-1]
            store()
    def OnPiscine2():
        global etat2
        if  B2.config('text')[-1]=='Off':
            B2.config(text='On ')
            etat2=B2.config('text')[-1]
            store()
        else:
            B2.config(text='Off')
            etat2=B2.config('text')[-1]
            store()
    def OnRobot():
        global etat3
        if  B3.config('text')[-1]=='Off':
            B3.config(text='On ')
            etat3=B3.config('text')[-1]
            store()
        else:
            B3.config(text='Off')
            etat3=B3.config('text')[-1]
            store()
    def OnChauffage():
        global etat4
        if  B4.config('text')[-1]=='Off':
            B4.config(text='On ')
            etat4=B4.config('text')[-1]
            store()
        else:
            B4.config(text='Off')
            etat4=B4.config('text')[-1]
            store()
            
    """buttons forçage"""
    def FOnLampe():
        if  B5.config('text')[-1]=='Off':
            B5.config(text='On ')
        else:
            B5.config(text='Off')        
    def FOnPiscine():
        if  B6.config('text')[-1]=='Off':
            B6.config(text='On ')
        else:
            B6.config(text='Off')
    def FOnPiscine2():
        if  B7.config('text')[-1]=='Off':
            B7.config(text='On ')
        else:
            B7.config(text='Off')
    def FOnRobot():
        if  B8.config('text')[-1]=='Off':
            B8.config(text='On ')
            
        else:
            B8.config(text='Off')
    def FOnChauffage():
        if  B9.config('text')[-1]=='Off':
            B9.config(text='On ')
          
        else:
            B9.config(text='Off')

    #local gpio button
    #If not GPIO.input(22):
    #    FOnPiscine()
        
    #Labels column1
    bai1 = ttk.Label(mainWin, width=13, text='Piscine: ')
    bai1.grid(row=2,column=1)
    bai2 = ttk.Label(mainWin, width=13, text='Piscine2: ')
    bai2.grid(row=3,column=1)
    bai3 = ttk.Label(mainWin, width=13, text='Robot: ')
    bai3.grid(row=4,column=1)
    bai4 = ttk.Label(mainWin, width=13, text='Chauffage: ')
    bai4.grid(row=5,column=1)
    label10 = ttk.Label(mainWin, width=13)#heure
    label10.grid(row=8,column=1)

    #Buttons Column 2
    B1 = ttk.Button( text ="On ", command = OnPiscine)
    B1.grid(row=2,column=2)
    B2 = ttk.Button( text ="On ", command = OnPiscine2)
    B2.grid(row=3,column=2)
    B3 = ttk.Button( text ="On ", command = OnRobot)
    B3.grid(row=4,column=2)
    B4 = ttk.Button( text ="On ", command = OnChauffage)
    B4.grid(row=5,column=2)


    #Labels column2

    labelai12 = ttk.Label(mainWin, width=13,text='Programmation horaire')
    labelai12.grid(row=1,column=2)


    #Labels column3
    labelai1 = ttk.Label(mainWin, width=7,text='Debut: ')
    labelai1.grid(row=2,column=3)
    labelai2 = ttk.Label(mainWin, width=7,text='Debut: ')
    labelai2.grid(row=3,column=3)

    #Entry Column4
    var6 = tk.StringVar()
    HOnPiscine = ttk.Entry(mainWin, width=8,textvariable=var6)
    HOnPiscine.grid(row=2,column=4)
    HOnPiscine.insert(0,'7:00:00')
    var6.trace("w",store)

    var7 = tk.StringVar()
    HOnPiscine2= ttk.Entry(mainWin, width=8,textvariable=var7)
    HOnPiscine2.grid(row=3,column=4)
    HOnPiscine2.insert(0,'7:10:00')
    var7.trace("w",store)

    #Labels Column5
    labelai1 = ttk.Label(mainWin, width=4,text=' Fin: ')
    labelai1.grid(row=2,column=5)
    labelai2 = ttk.Label(mainWin, width=4,text=' Fin: ')
    labelai2.grid(row=3,column=5)
    
    #Labels Column6
    labelai50 = ttk.Label(mainWin, width=8,text=' Robot: ')
    labelai50.grid(row=4,column=6)
    labelai51 = ttk.Label(mainWin, width=8,text=' Chauffage ')
    labelai51.grid(row=5,column=6)
    labelai61 = ttk.Label(mainWin, width=8,text=' Lampe ')
    labelai61.grid(row=6,column=6)        

    #Entry column6
    var = tk.StringVar()
    HOffPiscine= ttk.Entry(mainWin, width=8,textvariable=var)
    HOffPiscine.grid(row=2,column=6)
    HOffPiscine.insert(0,'7:01:00')
    var.trace("w",store)

    var1 = tk.StringVar()
    HOffPiscine2= ttk.Entry(mainWin, width=8,textvariable=var1)
    HOffPiscine2.grid(row=3,column=6)
    HOffPiscine2.insert(0,'7:11:00')
    var1.trace("w",store)

    #labels column7
    labelai11 = ttk.Label(mainWin, width=7,text='Forçage')
    labelai11.grid(row=1,column=7)
    bai6 = ttk.Label(mainWin, width=13, text='digit input: ')
    bai6.grid(row=7,column=7)
    bai7 = ttk.Label(mainWin, width=13, text='digit output: ')
    bai7.grid(row=8,column=7)

    #Buttons Column 7
    B6 = ttk.Button( text ="Off", command = FOnPiscine)
    B6.grid(row=2,column=7)
    B7 = ttk.Button( text ="Off", command = FOnPiscine2)
    B7.grid(row=3,column=7)
    B8 = ttk.Button( text ="Off", command = FOnRobot)
    B8.grid(row=4,column=7)
    B9 = ttk.Button( text ="Off", command = FOnChauffage)
    B9.grid(row=5,column=7)
    B5 = ttk.Button( text ="Off", command = FOnLampe)
    B5.grid(row=6,column=7)
    

    ## checkbox column 8 -> 14
    labelai13 = ttk.Label(mainWin, width=6,text='JOURS')
    labelai13.grid(row=1,column=8)
    vars=[]
    checkboxNames=['L1','Ma1','Me1','J1','V1','S1','D1',
                   'L2','Ma2','Me2','J2','V2','S2','D2']
           
    i=0
    k=0
    for j in range (0,14):
            vars.append(tk.IntVar())
            name= ttk.Checkbutton(mainWin,width=4,text=checkboxNames[j] ,variable =vars[j] )
            name.grid(row=[k+2],column=[i+8])
            i=i+1
            if i!=0 and i%7== 0:
                i=0
                k=k+1
    ##### load parameters #####        
    load()
    #######################################################################################################
    # Instancie la classe modbus
    mod = modbus()
    #Instancie la classe bmp085
    bmp085= i2cbmp085()
    # Instancie la classe serial reader
    serial = readFromSerial()
    # Instancie la classe ds18b20
    onewire = ds18b20()
    # Instancie la classe custartd
    custardanalog = analogcustard()
    
    # démarre les threads
    mod.start()
    bmp085.start()
    serial.start()
    onewire.start()
    custardanalog.start()
    update_Out()
    mainWin.mainloop()

    
    
    
  
