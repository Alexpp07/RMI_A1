
from random import randint
from re import T
import sys

from traitlets import Integer
from croblink import *
from math import *
import xml.etree.ElementTree as ET

CELLROWS=7
CELLCOLS=14

class MyRob(CRobLinkAngs):
    def __init__(self, rob_name, rob_id, angles, host):
        CRobLinkAngs.__init__(self, rob_name, rob_id, angles, host)
        

    # In this map the center of cell (i,j), (i in 0..6, j in 0..13) is mapped to labMap[i*2][j*2].
    # to know if there is a wall on top of cell(i,j) (i in 0..5), check if the value of labMap[i*2+1][j*2] is space or not
    def setMap(self, labMap):
        self.labMap = labMap

    def printMap(self):
        for l in reversed(self.labMap):
            print(''.join([str(l) for l in l]))

    def run(self):
        if self.status != 0:
            print("Connection refused or error")
            quit()
        
        state = 'stop'
        stopped_state = 'run'

        traceMap = []

        self.map2analyse = []

        for x in range(21):
            minimap = []
            for y in range(49):
                if x==11 and y==25: # initial position (mid map)
                    minimap.append('I')
                minimap.append(' ')
            traceMap.append(minimap)

        for x in range(21):
            mini = []
            for y in range(49):
                mini.append(' ')
            self.map2analyse.append(mini)

        posInitialX = ''
        posInitialY = ''
        self.prevPosX = ''
        self.prevPosY = ''
        count = 0
        self.intersections = []

        while True:
            f = open("minimap.txt", 'w')
            file2 = open("mini.txt", 'w')

            self.readSensors()

            if posInitialX=='' and posInitialY=='':
                posInitialX = self.measures.x
                posInitialY = self.measures.y

            if self.prevPosX=='' and self.prevPosY=='':
                self.prevPosX = self.measures.x
                self.prevPosY = self.measures.y

            posMidX = 25
            posMidY = 11

            difX = posInitialX - self.measures.x
            difY = posInitialY - self.measures.y

            x = int(posMidX) - int(round(difX,0))
            y = int(posMidY) + int(round(difY,0))

    
            self.map2analyse[y][x] = '-'

            if -5 <= self.measures.compass <= 5: #DIREITA
                if traceMap[y][x]==' ' and (traceMap[y][x-1]==' ' or traceMap[y][x-1]=='I') and (traceMap[y][x+1]==' ' or traceMap[y][x+1]=='I') and (traceMap[y-1][x]==' ' or traceMap[y-1][x]=='I') and (traceMap[y+1][x]==' ' or traceMap[y+1][x]=='I'):
                    traceMap[y][x] = '-'
            elif -95 <= self.measures.compass <= -85: #BAIXO
                if traceMap[y][x]==' ' and (traceMap[y][x-1]==' ' or traceMap[y][x-1]=='I') and (traceMap[y][x+1]==' ' or traceMap[y][x+1]=='I') and (traceMap[y-1][x]==' ' or traceMap[y-1][x]=='I') and (traceMap[y+1][x]==' ' or traceMap[y+1][x]=='I'):
                    traceMap[y][x] = '|'
            elif -180 <= self.measures.compass <= -175 or 175 <= self.measures.compass <= 180: #ESQUERDA
                if traceMap[y][x]==' ' and (traceMap[y][x-1]==' ' or traceMap[y][x-1]=='I') and (traceMap[y][x+1]==' ' or traceMap[y][x+1]=='I') and (traceMap[y-1][x]==' ' or traceMap[y-1][x]=='I') and (traceMap[y+1][x]==' ' or traceMap[y+1][x]=='I'):
                    traceMap[y][x] = '-'
            elif 85 <= self.measures.compass <= 95: #CIMA
                if traceMap[y][x]==' ' and (traceMap[y][x-1]==' ' or traceMap[y][x-1]=='I') and (traceMap[y][x+1]==' ' or traceMap[y][x+1]=='I') and (traceMap[y-1][x]==' ' or traceMap[y-1][x]=='I') and (traceMap[y+1][x]==' ' or traceMap[y+1][x]=='I'):
                 traceMap[y][x] = '|'

            # print(allMap)

            for x in range(21):
                for y in range(49):
                    f.write(traceMap[x][y])
                f.write('\n')

            f.close

            for x in range(21):
                for y in range(49):
                    file2.write(self.map2analyse[x][y])
                file2.write('\n')

            file2.close

            if self.measures.endLed:
                print(self.rob_name + " exiting")
                quit()

            if state == 'stop' and self.measures.start:
                state = stopped_state

            if state != 'stop' and self.measures.stop:
                stopped_state = state
                state = 'stop'

            if state == 'run':
                if self.measures.visitingLed==True:
                    state='wait'
                if self.measures.ground==0:
                    self.setVisitingLed(True)
                count+=1
                self.wander(traceMap,posInitialX,posInitialY,count)
            elif state=='wait':
                self.setReturningLed(True)
                if self.measures.visitingLed==True:
                    self.setVisitingLed(False)
                if self.measures.returningLed==True:
                    state='return'
                self.driveMotors(0.0,0.0)
            elif state=='return':
                if self.measures.visitingLed==True:
                    self.setVisitingLed(False)
                if self.measures.returningLed==True:
                    self.setReturningLed(False)
                count+=1
                self.wander(traceMap,posInitialX,posInitialY,count)
            

    def wander(self,traceMap,posInitialX,posInitialY,count):
        center_id = 0
        left_id = 1
        right_id = 2
        back_id = 3

        posMidX = 25
        posMidY = 11

        if    self.measures.irSensor[center_id] > 5.0\
           or self.measures.irSensor[left_id]   > 5.0\
           or self.measures.irSensor[right_id]  > 5.0\
           or self.measures.irSensor[back_id]   > 5.0:
            print('Rotate left')
            self.driveMotors(-0.1,+0.1)
        elif self.measures.irSensor[left_id]> 2.7:
            print('Rotate slowly right')
            self.driveMotors(0.1,0.0)
        elif self.measures.irSensor[right_id]> 2.7:
            print('Rotate slowly left')
            self.driveMotors(0.0,0.1)
        else:
            difX = posInitialX - self.measures.x
            difY = posInitialY - self.measures.y

            x = int(posMidX) - int(round(difX,0))
            y = int(posMidY) + int(round(difY,0))

            print(self.measures.lineSensor)
            print("----------------------------")
            print(self.intersections)
            print("----------------------------")


            if self.measures.lineSensor[0]=='1' and self.measures.lineSensor[1]=='1' and self.measures.lineSensor[2]=='1' and self.measures.lineSensor[3]=='1' and self.measures.lineSensor[4]=='1' and self.measures.lineSensor[5]=='1' and self.measures.lineSensor[6]=='1':
                if (-10 <= self.measures.compass <= 10): #DIREITA
                    if self.map2analyse[y-1][x]=='-' or self.map2analyse[y+1][x]=='-' and self.map2analyse[y][x+1]=='-':
                        """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                        print("AQUIIIIIIdireita")
                        pass
                    elif (self.map2analyse[y-1][x]=='-' or self.map2analyse[y+1][x]!='-') and self.map2analyse[y][x+1]=='x':
                        self.driveMotors(0.10,0.10)
                    elif (self.map2analyse[y-1][x]=='-' or self.map2analyse[y+1][x]!='-') and self.map2analyse[y][x+1]==' ':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y-1][x] != '-':
                                self.map2analyse[y-1][x] = 'x'
                                if (y,x) not in self.intersections:
                                    self.intersections.append((y,x))
                            if self.map2analyse[y+1][x] != '-':
                                self.map2analyse[y+1][x] = 'x'
                                if (y,x) not in self.intersections:
                                    self.intersections.append((y,x))
                        else:
                            if self.map2analyse[y-1][x]=='-' and self.map2analyse[y+1][x]!='-':
                                self.driveMotors(0.15,-0.15)
                            elif self.map2analyse[y-1][x]!='-' and self.map2analyse[y+1][x]=='-':
                                self.driveMotors(-0.15,0.15)
                            elif self.map2analyse[y-1][x]=='-' and self.map2analyse[y+1][x]=='-':
                                """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                                print("AQUIIIIIIdireita2")
                                self.move_in_line()
                    elif (self.map2analyse[y-1][x]=='-' or self.map2analyse[y+1][x]!='-') and self.map2analyse[y][x+1]=='-':
                        if self.map2analyse[y-1][x]=='-' and self.map2analyse[y+1][x]!='-':
                            self.driveMotors(0.15,-0.15)
                        elif self.map2analyse[y-1][x]!='-' and self.map2analyse[y+1][x]=='-':
                            self.driveMotors(-0.15,0.15)
                        elif self.map2analyse[y-1][x]=='-' and self.map2analyse[y+1][x]=='-':
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            print("AQUIIIIIIdireita3")
                            self.move_in_line()
                    elif (self.map2analyse[y-1][x]==' ' and self.map2analyse[y+1][x]==' ' and self.map2analyse[y][x+1]==' ') or self.map2analyse[y][x+1]=='x':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y-1][x] != '-':
                                self.map2analyse[y-1][x] = 'x'
                                if (y,x) not in self.intersections:
                                    self.intersections.append((y,x))
                            if self.map2analyse[y+1][x] != '-':
                                self.map2analyse[y+1][x] = 'x'
                                if (y,x) not in self.intersections:
                                    self.intersections.append((y,x))
                        else:
                            self.driveMotors(-0.15,-0.10)
                    elif self.map2analyse[y-1][x]=='x':
                        self.driveMotors(-0.1,0.1)
                    elif self.map2analyse[y+1][x]=='x':
                        self.driveMotors(0.1,-0.1)
                    else:
                        self.move_in_line()
                elif (-180 <= self.measures.compass <= -170 or 170 <= self.measures.compass <= 180): #ESQUERDA
                    if self.map2analyse[y-1][x]=='-' and self.map2analyse[y+1][x]=='-' and self.map2analyse[y][x-1]=='-':
                        """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                        print("AQUIIIIIIesquerda")
                        pass
                    elif (self.map2analyse[y-1][x]=='-' or self.map2analyse[y+1][x]=='-') and self.map2analyse[y][x-1]=='x':
                        self.driveMotors(0.10,0.10)
                    elif (self.map2analyse[y-1][x]=='-' or self.map2analyse[y+1][x]=='-') and self.map2analyse[y][x+1]==' ':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y-1][x] != '-':
                                self.map2analyse[y-1][x] = 'x'
                                if (y,x) not in self.intersections:
                                    self.intersections.append((y,x))
                            if self.map2analyse[y+1][x] != '-':
                                self.map2analyse[y+1][x] = 'x'
                                if (y,x) not in self.intersections:
                                    self.intersections.append((y,x))
                        else:
                            if self.map2analyse[y-1][x]=='-' and self.map2analyse[y+1][x]!='-':
                                self.driveMotors(-0.15,0.15)
                            elif self.map2analyse[y-1][x]!='-' and self.map2analyse[y+1][x]=='-':
                                self.driveMotors(0.15,-0.15)
                            elif self.map2analyse[y-1][x]=='-' and self.map2analyse[y+1][x]=='-':
                                """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                                print("AQUIIIIIIesquerda2")
                                self.move_in_line()
                    elif (self.map2analyse[y-1][x]=='-' or self.map2analyse[y+1][x]=='-') and self.map2analyse[y][x+1]=='-':
                        if self.map2analyse[y-1][x]=='-' and self.map2analyse[y+1][x]!='-':
                            self.driveMotors(-0.15,0.15)
                        elif self.map2analyse[y-1][x]!='-' and self.map2analyse[y+1][x]=='-':
                            self.driveMotors(0.15,-0.15)
                        elif self.map2analyse[y-1][x]=='-' and self.map2analyse[y+1][x]=='-':
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            print("AQUIIIIIIesquerda3")
                            self.move_in_line()
                    elif (self.map2analyse[y-1][x]==' ' and self.map2analyse[y+1][x]==' ' and self.map2analyse[y][x-1]==' ') or self.map2analyse[y][x-1]=='x':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y-1][x] != '-':
                                self.map2analyse[y-1][x] = 'x'
                                if (y,x) not in self.intersections:
                                    self.intersections.append((y,x))
                            if self.map2analyse[y+1][x] != '-':
                                self.map2analyse[y+1][x] = 'x'
                                if (y,x) not in self.intersections:
                                    self.intersections.append((y,x))
                        else:
                            self.driveMotors(-0.15,-0.10)
                    elif self.map2analyse[y-1][x]=='x':
                        self.driveMotors(0.1,-0.1)
                    elif self.map2analyse[y+1][x]=='x':
                        self.driveMotors(-0.1,0.1)
                    else:
                        self.move_in_line()
                elif (-100 <= self.measures.compass <= -80): #BAIXO
                    if self.map2analyse[y][x-1]=='-' and self.map2analyse[y][x+1]=='-' and self.map2analyse[y+1][x]=='-':
                        """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                        print("AQUIIIIIIbaixo")
                        pass
                    elif (self.map2analyse[y][x-1]=='-' or self.map2analyse[y][x+1]=='-') and self.map2analyse[y+1][x]=='x':
                        self.driveMotors(0.10,0.10)
                    elif (self.map2analyse[y][x-1]=='-' or self.map2analyse[y][x+1]=='-') and self.map2analyse[y+1][x]==' ':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y][x-1] != '-':
                                self.map2analyse[y][x-1] = 'x'
                                if (y,x) not in self.intersections:
                                    self.intersections.append((y,x))
                            if self.map2analyse[y][x+1] != '-':
                                self.map2analyse[y][x+1] = 'x'
                                if (y,x) not in self.intersections:
                                    self.intersections.append((y,x))
                        else:
                            if self.map2analyse[y][x-1]=='-' and self.map2analyse[y][x+1]!='-':
                                self.driveMotors(-0.15,0.15)
                            elif self.map2analyse[y][x-1]!='-' and self.map2analyse[y][x+1]=='-':
                                self.driveMotors(0.15,-0.15)
                            elif self.map2analyse[y][x-1]=='-' and self.map2analyse[y][x+1]=='-':
                                """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                                print("AQUIIIIIIbaixo2")
                                self.move_in_line()
                    elif (self.map2analyse[y][x-1]=='-' or self.map2analyse[y][x+1]=='-') and self.map2analyse[y+1][x]=='-':
                        if self.map2analyse[y][x-1]=='-' and self.map2analyse[y][x+1]!='-':
                            self.driveMotors(-0.15,0.15)
                        elif self.map2analyse[y][x-1]!='-' and self.map2analyse[y][x+1]=='-':
                            self.driveMotors(0.15,-0.15)
                        elif self.map2analyse[y][x-1]=='-' and self.map2analyse[y][x+1]=='-':
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            print("AQUIIIIIIbaixo3")
                            self.move_in_line()
                    elif (self.map2analyse[y][x-1]==' ' and self.map2analyse[y][x+1]==' ' and self.map2analyse[y+1][x]==' ') or self.map2analyse[y+1][x]=='x':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y][x-1] != '-':
                                self.map2analyse[y][x-1] = 'x'
                                if (y,x) not in self.intersections:
                                    self.intersections.append((y,x))
                            if self.map2analyse[y][x+1] != '-':
                                self.map2analyse[y][x+1] = 'x'
                                if (y,x) not in self.intersections:
                                    self.intersections.append((y,x))
                        else:
                            self.driveMotors(-0.15,-0.10)
                    elif self.map2analyse[y][x-1]=='x':
                        self.driveMotors(0.1,-0.1)
                    elif self.map2analyse[y][x+1]=='x':
                        self.driveMotors(-0.1,0.1)
                    else:
                        self.move_in_line()
                elif (80 <= self.measures.compass <= 100): #CIMA
                    if self.map2analyse[y][x-1]=='-' and self.map2analyse[y][x+1]=='-' and self.map2analyse[y-1][x]=='-':
                        """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                        print("AQUIIIIIIcima")
                        self.move_in_line()
                    elif (self.map2analyse[y][x-1]=='-' or self.map2analyse[y][x+1]=='-') and self.map2analyse[y-1][x]=='x':
                        self.driveMotors(0.10,0.10)
                    elif (self.map2analyse[y][x-1]=='-' or self.map2analyse[y][x+1]=='-') and self.map2analyse[y-1][x]==' ':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y][x-1] != '-':
                                self.map2analyse[y][x-1] = 'x'
                                if (y,x) not in self.intersections:
                                    self.intersections.append((y,x))
                            if self.map2analyse[y][x+1] != '-':
                                self.map2analyse[y][x+1] = 'x'
                                if (y,x) not in self.intersections:
                                    self.intersections.append((y,x))
                        else:
                            if self.map2analyse[y][x-1]=='-' and self.map2analyse[y][x+1]!='-':
                                self.driveMotors(0.15,-0.15)
                            elif self.map2analyse[y][x-1]!='-' and self.map2analyse[y][x+1]=='-':
                                self.driveMotors(-0.15,0.15)
                            elif self.map2analyse[y][x-1]=='-' and self.map2analyse[y][x+1]=='-':
                                """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                                print("AQUIIIIIIcima2")
                                self.move_in_line()
                    elif (self.map2analyse[y][x-1]=='-' or self.map2analyse[y][x+1]=='-') and self.map2analyse[y-1][x]=='-':
                        if self.map2analyse[y][x-1]=='-' and self.map2analyse[y][x+1]!='-':
                            self.driveMotors(0.15,-0.15)
                        elif self.map2analyse[y][x-1]!='-' and self.map2analyse[y][x+1]=='-':
                            self.driveMotors(-0.15,0.15)
                        elif self.map2analyse[y][x-1]=='-' and self.map2analyse[y][x+1]=='-':
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            print("AQUIIIIIIcima3")
                            self.move_in_line()
                    elif (self.map2analyse[y][x-1]==' ' and self.map2analyse[y][x+1]==' ' and self.map2analyse[y-1][x]==' ') or self.map2analyse[y-1][x]=='x':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y][x-1] != '-':
                                self.map2analyse[y][x-1] = 'x'
                                if (y,x) not in self.intersections:
                                    self.intersections.append((y,x))
                            if self.map2analyse[y][x+1] != '-':
                                self.map2analyse[y][x+1] = 'x'
                                if (y,x) not in self.intersections:
                                    self.intersections.append((y,x))
                        else:
                            self.driveMotors(-0.15,-0.10)
                    elif self.map2analyse[y][x-1]=='x':
                        self.driveMotors(-0.1,0.1)
                    elif self.map2analyse[y][x+1]=='x':
                        self.driveMotors(0.1,-0.1)
                    else:
                        self.move_in_line()
            elif self.measures.lineSensor[0]=='1' and self.measures.lineSensor[1]=='1' and self.measures.lineSensor[2]=='1' and self.measures.lineSensor[3]=='1' and self.measures.lineSensor[4]=='1' and self.measures.lineSensor[5]=='0' and self.measures.lineSensor[6]=='0':
                if (-5 <= self.measures.compass <= 5): #DIREITA
                    if self.map2analyse[y-1][x]=='-':
                        if self.map2analyse[y][x+1]!='-':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                pass
                        else:
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            self.driveMotors(-0.15,0.15)      
                    elif (self.map2analyse[y-1][x]==' ' and self.map2analyse[y][x+1]==' ') or self.map2analyse[y][x+1]=='x':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y-1][x] != '-':
                                self.map2analyse[y-1][x] = 'x'
                                if (y,x) not in self.intersections:
                                    self.intersections.append((y,x))
                        else:
                            self.driveMotors(-0.15,0.15)
                    elif self.map2analyse[y-1][x]=='x':
                        self.driveMotors(-0.1,0.1)
                    elif self.map2analyse[y-1][x]=='-':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            pass
                        else:
                            self.driveMotors(-0.1,0.1)
                    else:
                        self.move_in_line()
                elif (-180 <= self.measures.compass <= -175 or 175 <= self.measures.compass <= 180): #ESQUERDA
                    """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                    if self.map2analyse[y+1][x]=='-':
                        if self.map2analyse[y][x-1]!='-':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                pass
                        else:
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            self.driveMotors(-0.15,0.15) 
                    elif (self.map2analyse[y+1][x]==' ' and self.map2analyse[y][x-1]==' ') or self.map2analyse[y][x-1]=='x':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y+1][x] != '-':
                                self.map2analyse[y+1][x] = 'x'
                                if (y,x) not in self.intersections:
                                    self.intersections.append((y,x))
                        else:
                            self.driveMotors(-0.15,0.15)
                    elif self.map2analyse[y+1][x]=='x':
                        self.driveMotors(-0.1,0.1)
                    elif self.map2analyse[y+1][x]=='-':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            pass
                        else:
                            self.driveMotors(-0.1,0.1)
                    else:
                        self.move_in_line()
                elif (-95 <= self.measures.compass <= -85): #BAIXO
                    """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                    if self.map2analyse[y][x+1]=='-':
                        if self.map2analyse[y+1][x]!='-':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                pass
                        else:
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            self.driveMotors(-0.15,0.15) 
                    elif (self.map2analyse[y][x+1]==' ' and self.map2analyse[y+1][x]==' ') or self.map2analyse[y+1][x]=='x':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y][x+1] != '-':
                                self.map2analyse[y][x+1] = 'x'
                                if (y,x) not in self.intersections:
                                    self.intersections.append((y,x))
                        else:
                            self.driveMotors(-0.15,0.15)
                    elif self.map2analyse[y][x+1]=='x':
                        self.driveMotors(-0.1,0.1)
                    elif self.map2analyse[y][x+1]=='-':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            pass
                        else:
                            self.driveMotors(-0.1,0.1)
                    else:
                        self.move_in_line()
                elif (85 <= self.measures.compass <= 95): #CIMA
                    """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                    if self.map2analyse[y][x-1]=='-':
                        if self.map2analyse[y-1][x]!='-':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                pass
                        else:
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            self.driveMotors(-0.15,0.15) 
                    elif (self.map2analyse[y][x-1]==' ' and self.map2analyse[y-1][x]==' ') or self.map2analyse[y-1][x]=='x':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y][x-1] != '-':
                                self.map2analyse[y][x-1] = 'x'
                                if (y,x) not in self.intersections:
                                    self.intersections.append((y,x))
                        else:
                            self.driveMotors(-0.15,0.15)
                    elif self.map2analyse[y][x-1]=='x':
                        self.driveMotors(-0.1,0.1)
                    elif self.map2analyse[y][x-1]=='-':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            pass
                        else:
                            self.driveMotors(-0.1,0.1)
                    else:
                        self.move_in_line()
            elif self.measures.lineSensor[0]=='0' and self.measures.lineSensor[1]=='0' and self.measures.lineSensor[2]=='1' and self.measures.lineSensor[3]=='1' and self.measures.lineSensor[4]=='1' and self.measures.lineSensor[5]=='1' and self.measures.lineSensor[6]=='1':
                if (-5 <= self.measures.compass <= 5): #DIREITA
                    """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                    if self.map2analyse[y+1][x]=='-':
                        if self.map2analyse[y][x+1]!='-':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                pass
                        else:
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            self.driveMotors(0.15,-0.15)
                    elif (self.map2analyse[y+1][x]==' ' and self.map2analyse[y][x+1]==' ') or self.map2analyse[y][x+1]=='x':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y+1][x] != '-':
                                self.map2analyse[y+1][x] = 'x'
                                if (y,x) not in self.intersections:
                                    self.intersections.append((y,x))
                        else:
                            self.driveMotors(0.15,-0.15)
                    elif self.map2analyse[y+1][x]=='x':
                        self.driveMotors(0.1,-0.1)
                    elif self.map2analyse[y+1][x]=='-':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            pass
                        else:
                            self.driveMotors(0.1,-0.1)
                    else:
                        self.move_in_line()
                elif (-180 <= self.measures.compass <= -175 or 175 <= self.measures.compass <= 180): #ESQUERDA
                    """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                    if self.map2analyse[y-1][x]=='-':
                        if self.map2analyse[y][x-1]!='-':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                pass
                        else:
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            self.driveMotors(0.15,-0.15)
                    elif (self.map2analyse[y-1][x]==' ' and self.map2analyse[y][x-1]==' ') or self.map2analyse[y][x-1]=='x':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y-1][x] != '-':
                                self.map2analyse[y-1][x] = 'x'
                                if (y,x) not in self.intersections:
                                    self.intersections.append((y,x))
                        else:
                            self.driveMotors(0.15,-0.15)
                    elif self.map2analyse[y-1][x]=='x':
                        self.driveMotors(0.1,-0.1)
                    elif self.map2analyse[y-1][x]=='-':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            pass
                        else:
                            self.driveMotors(0.1,-0.1)
                    else:
                        self.move_in_line()
                elif (-95 <= self.measures.compass <= -85): #BAIXO
                    """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                    if self.map2analyse[y][x-1]=='-':
                        if self.map2analyse[y+1][x]!='-':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                pass
                        else:
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            self.driveMotors(0.15,-0.15)
                    elif (self.map2analyse[y][x-1]==' ' and self.map2analyse[y+1][x]==' ') or self.map2analyse[y+1][x]=='x':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y][x-1] != '-':
                                self.map2analyse[y][x-1] = 'x'
                                if (y,x) not in self.intersections:
                                    self.intersections.append((y,x))
                        else:
                            self.driveMotors(0.15,-0.15)
                    elif self.map2analyse[y][x-1]=='x':
                        self.driveMotors(0.1,-0.1)
                    elif self.map2analyse[y][x-1]=='-':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            pass
                        else:
                            self.driveMotors(0.1,-0.1)
                    else:
                        self.move_in_line()
                elif (85 <= self.measures.compass <= 95): #CIMA
                    """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                    if self.map2analyse[y][x+1]=='-':
                        if self.map2analyse[y-1][x]!='-':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                pass
                        else:
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            self.driveMotors(0.15,-0.15)
                    elif (self.map2analyse[y][x+1]==' ' and self.map2analyse[y-1][x]==' ') or self.map2analyse[y-1][x]=='x':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y][x+1] != '-':
                                self.map2analyse[y][x+1] = 'x'
                                if (y,x) not in self.intersections:
                                    self.intersections.append((y,x))
                        else:
                            self.driveMotors(0.15,-0.15)
                    elif self.map2analyse[y][x+1]=='x':
                        self.driveMotors(0.1,-0.1)
                    elif self.map2analyse[y][x+1]=='-':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            pass
                        else:
                            self.driveMotors(0.1,-0.1)
                    else:
                        self.move_in_line()
            else:
                self.move_in_line()

    def check_if_still_intersection(self,x,y): #Checks if (y,x) is still a point of intersection, that is, if the adjacent points still have x's
        if self.map2analyse[y][x+1]=='x' or self.map2analyse[y][x-1]=='x' or self.map2analyse[y+1][x]=='x' or self.map2analyse[y-1][x]=='x':
            return True
        else:
            self.intersections.remove((y,x))
            return False


    def get_nearest_intersection(self,currentX,currentY):
        #Given a list of coordinates for the places i wanna go, I have to find the nearest intersection
        distance = -1
        bestX = ''
        bestY = ''
        for (savedY,savedX) in self.intersections:
            temp = sqrt(((savedY - currentY)**2) + ((savedX - currentX)**2))
            if distance == -1:
                distance = temp
                bestX = savedX
                bestY = savedY
            else:
                if temp < distance:
                    distance = temp
                    bestX = savedX
                    bestY = savedY
        #Now distance is the real distance between two points
        self.intersections.remove((bestY,bestX))
        #Now the robot should go for Y,X    
        bin_matrix = []
        for y in self.map2analyse:
            temp = []
            for t in y:
                if t == '-':
                    temp.append('1')
                else:
                    temp.append('0')
            bin_matrix.append(temp)

        self.find_path(currentX,currentY,bestX,bestY,bin_matrix)


    #Given a matrix of 0's and 1's, bin_matrix, i want to find the path from bin_matrix[currentY][currentX] to bin_matrix[bestY][bestX] only passing through 1's
    def find_path(self,currentX,currentY,bestX,bestY,bin_matrix):
        
        node_initial = Node(None,(currentY,currentX),0,0,0)
        end_node = Node(None,(bestY,bestX),0,0,0)

        open_list=[]
        closed_list = []

        open_list.append(node_initial)

        while len(open_list) > 0:
            current_node = open_list[0]
            current_index = 0
            for index,item in enumerate(open_list):
                if item.f < current_node.f:
                    current_node = item
                    current_index = index

            open_list.pop(current_index)
            closed_list.append(current_node)

            if current_node == end_node:
                path = []
                current = current_node
                while current is not None:
                    path.append(current.position)
                    current = current.parent
                return path[::-1]

            children = []
            for new_position in [(0,-1),(0,1),(-1,0),(1,0)]:
                node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])
                if node_position[0] > (len(bin_matrix) - 1) or node_position[0] < 0 or node_position[1] > (len(bin_matrix[len(bin_matrix)-1]) -1) or node_position[1] < 0:
                    continue
                if bin_matrix[node_position[0]][node_position[1]] == '0':
                    continue
                new_node = Node(current_node, node_position)
                children.append(new_node)

            for child in children:
                for closed_child in closed_list:
                    if child == closed_child:
                        continue
                child.g = current_node.g + 1
                child.h = sqrt(((child.position[0] - end_node.position[0])**2) + ((child.position[1] - end_node.position[1])**2))
                child.f = child.g + child.h
                for open_node in open_list:
                    if child == open_node and child.g > open_node.g:
                        continue
                open_list.append(child)



        
        


    # def find_path(self,currentX,currentY,goalX,goalY):
    #     #This function will find the path from the current position to the goal position
    #     #The path will be saved in a list of coordinates
        
    #Function that, given a current position (currentY,currentX) will find the best path to the goal position (goalY,goalX)
    #The available paths are marked with '-' and '|' on the 'mini.txt' file and the path must only include coordinates that have those characters
    #The path will be saved in a list of coordinates
    # def find_path(self,currentX,currentY,goalX,goalY):
    #     #This function will find the path from the current position to the goal position
    #     #The path will be saved in a list of coordinates
    #     self.path = []
    #     self.path.append((currentY,currentX))
    #     if currentX == goalX and currentY == goalY:
    #         return
    #     if currentX < goalX:
    #         self.find_path(currentX+1,currentY,goalX,goalY)
    #     elif currentX > goalX:
    #         self.find_path(currentX-1,currentY,goalX,goalY)
    #     elif currentY < goalY:
    #         self.find_path(currentX,currentY+1,goalX,goalY)
    #     elif currentY > goalY:
    #         self.find_path(currentX,currentY-1,goalX,goalY)
    #     else:
    #         return
    #     self.path.append((currentY,currentX))
    #     return

    def move_in_line(self):
        if self.measures.lineSensor[0]=='0' and self.measures.lineSensor[1]=='0' and self.measures.lineSensor[2]=='1' and self.measures.lineSensor[3]=='1' and self.measures.lineSensor[4]=='1' and self.measures.lineSensor[5]=='0' and self.measures.lineSensor[6]=='0':
            self.driveMotors(0.10,0.10)
        elif self.measures.lineSensor[0]=='0' and self.measures.lineSensor[1]=='0' and self.measures.lineSensor[2]=='1' and self.measures.lineSensor[3]=='1' and self.measures.lineSensor[4]=='0' and self.measures.lineSensor[5]=='0' and self.measures.lineSensor[6]=='0':
            self.driveMotors(0.08,0.10)
        elif self.measures.lineSensor[0]=='0' and self.measures.lineSensor[1]=='0' and self.measures.lineSensor[2]=='0' and self.measures.lineSensor[3]=='1' and self.measures.lineSensor[4]=='1' and self.measures.lineSensor[5]=='0' and self.measures.lineSensor[6]=='0':
            self.driveMotors(0.10,0.08)
        elif self.measures.lineSensor[0]=='1' and self.measures.lineSensor[1]=='1':
            self.driveMotors(-0.10,0.10)
        elif self.measures.lineSensor[0]=='0' and self.measures.lineSensor[1]=='1':
            self.driveMotors(-0.06,0.10)
        elif self.measures.lineSensor[0]=='0' and self.measures.lineSensor[1]=='1':
                self.driveMotors(-0.06,0.10)
        elif self.measures.lineSensor[0]=='1' and self.measures.lineSensor[1]=='0':
                self.driveMotors(-0.10,0.10)
        elif self.measures.lineSensor[5]=='0' and self.measures.lineSensor[6]=='1':
            self.driveMotors(0.10,-0.10)
        elif self.measures.lineSensor[5]=='1' and self.measures.lineSensor[6]=='0':
            self.driveMotors(0.10,-0.06)
        elif self.measures.lineSensor[5]=='1' and self.measures.lineSensor[6]=='0':
            self.driveMotors(0.10,-0.06)
        elif self.measures.lineSensor[5]=='1' and self.measures.lineSensor[6]=='1':
            self.driveMotors(0.10,-0.10)
        elif self.measures.lineSensor[0]=='0' and self.measures.lineSensor[1]=='0' and self.measures.lineSensor[2]=='0' and self.measures.lineSensor[3]=='0' and self.measures.lineSensor[4]=='0' and self.measures.lineSensor[5]=='0' and self.measures.lineSensor[6]=='0':
            self.driveMotors(-0.02,-0.02)
        else:
            self.driveMotors(0.15,0.15)

class Map():
    def __init__(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        
        self.labMap = [[' '] * (CELLCOLS*2-1) for i in range(CELLROWS*2-1) ]
        i=1
        for child in root.iter('Row'):
           line=child.attrib['Pattern']
           row =int(child.attrib['Pos'])
           if row % 2 == 0:  # this line defines vertical lines
               for c in range(len(line)):
                   if (c+1) % 3 == 0:
                       if line[c] == '|':
                           self.labMap[row][(c+1)//3*2-1]='|'
                       else:
                           None
           else:  # this line defines horizontal lines
               for c in range(len(line)):
                   if c % 3 == 0:
                       if line[c] == '-':
                           self.labMap[row][c//3*2]='-'
                       else:
                           None
               
           i=i+1

class Node():
    def __init__(self,parent=None,position=None,g=0,h=0,f=0):
        self.parent = None
        self.position = None
        self.g = 0
        self.h = 0
        self.f = 0
    


rob_name = "pClient1"
host = "localhost"
pos = 1
mapc = None

for i in range(1, len(sys.argv),2):
    if (sys.argv[i] == "--host" or sys.argv[i] == "-h") and i != len(sys.argv) - 1:
        host = sys.argv[i + 1]
    elif (sys.argv[i] == "--pos" or sys.argv[i] == "-p") and i != len(sys.argv) - 1:
        pos = int(sys.argv[i + 1])
    elif (sys.argv[i] == "--robname" or sys.argv[i] == "-r") and i != len(sys.argv) - 1:
        rob_name = sys.argv[i + 1]
    elif (sys.argv[i] == "--map" or sys.argv[i] == "-m") and i != len(sys.argv) - 1:
        mapc = Map(sys.argv[i + 1])
    else:
        print("Unkown argument", sys.argv[i])
        quit()

if __name__ == '__main__':
    rob=MyRob(rob_name,pos,[0.0,60.0,-60.0,180.0],host)
    if mapc != None:
        rob.setMap(mapc.labMap)
        rob.printMap()
    
    rob.run()
