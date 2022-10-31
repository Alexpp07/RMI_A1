
from random import randint
import random
import sys
from time import sleep

from traitlets import Integer
from croblink import *
from math import *
import xml.etree.ElementTree as ET

CELLROWS=7
CELLCOLS=14

class MyRob(CRobLinkAngs):
    def __init__(self, rob_name, rob_id, angles, host,filename):
        CRobLinkAngs.__init__(self, rob_name, rob_id, angles, host)
        self.filename = filename
        

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
        self.setMap(traceMap)
        print("hello")
        self.printMap()

        self.map2analyse = []

        for x in range(21):
            minimap = []
            for y in range(49):
                if x==10 and y==24: # initial position (mid map)
                    minimap.append('I')
                minimap.append(' ')
            traceMap.append(minimap)
            self.setMap(traceMap)

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
        self.firstTime = True
        self.previousPoint = (0,0)
        self.playGame = True

        while self.playGame:
            f = open(self.filename, 'w')
            file2 = open("mini.txt", 'w')

            self.readSensors()

            if posInitialX=='' and posInitialY=='':
                posInitialX = self.measures.x
                posInitialY = self.measures.y

            if self.prevPosX=='' and self.prevPosY=='':
                self.prevPosX = self.measures.x
                self.prevPosY = self.measures.y

            posMidX = 24
            posMidY = 10

            self.MidX = 24
            self.MidY = 10

            difX = posInitialX - self.measures.x
            difY = posInitialY - self.measures.y

            x = int(posMidX) - int(round(difX,0))
            y = int(posMidY) + int(round(difY,0))

            self.currentPoint = (y,x)

    
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
            self.setMap(traceMap)

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

        posMidX = 24
        posMidY = 10

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
            currentPoint = self.currentPoint
            difX = posInitialX - self.measures.x
            difY = posInitialY - self.measures.y

            x = int(posMidX) - int(round(difX,0))
            y = int(posMidY) + int(round(difY,0))

            print(self.measures.lineSensor)

            if self.measures.lineSensor[0]=='1' and self.measures.lineSensor[1]=='1' and self.measures.lineSensor[2]=='1' and self.measures.lineSensor[3]=='1' and self.measures.lineSensor[4]=='1' and self.measures.lineSensor[5]=='1' and self.measures.lineSensor[6]=='1':
                if (-10 <= self.measures.compass <= 10): #DIREITA
                    if self.map2analyse[y-1][x]=='-' or self.map2analyse[y+1][x]=='-' and self.map2analyse[y][x+1]=='-':
                        """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                        currentPoint = (y,x)
                        destinyPoint = self.destinyPointFunc(currentPoint)
                        possible = ['up','right','down']
                        self.path_follow(currentPoint,destinyPoint,possible)
                    elif (self.map2analyse[y-1][x]=='-' or self.map2analyse[y+1][x]=='-') and self.map2analyse[y][x+1]=='x':
                        self.driveMotors(0.10,0.10)
                    elif (self.map2analyse[y-1][x]=='-' or self.map2analyse[y+1][x]=='-') and self.map2analyse[y][x+1]==' ':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y-1][x] != '-':
                                self.map2analyse[y-1][x] = 'x'
                            if self.map2analyse[y+1][x] != '-':
                                self.map2analyse[y+1][x] = 'x'
                        else:
                            if self.map2analyse[y-1][x]=='-' and self.map2analyse[y+1][x]!='-':
                                self.driveMotors(0.15,-0.15)
                                self.move_in_line()
                            elif self.map2analyse[y-1][x]!='-' and self.map2analyse[y+1][x]=='-':
                                self.driveMotors(-0.15,0.15)
                                self.move_in_line()
                            elif self.map2analyse[y-1][x]=='-' and self.map2analyse[y+1][x]=='-':
                                """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                                currentPoint = (y,x)
                                destinyPoint = self.destinyPointFunc(currentPoint)
                                possible = ['up','down']
                                self.path_follow(currentPoint,destinyPoint,possible)
                    elif (self.map2analyse[y-1][x]=='-' or self.map2analyse[y+1][x]=='-') and self.map2analyse[y][x+1]=='-':
                        if self.map2analyse[y-1][x]=='-' and self.map2analyse[y+1][x]!='-':
                            self.driveMotors(0.15,-0.15)
                            self.move_in_line()
                        elif self.map2analyse[y-1][x]!='-' and self.map2analyse[y+1][x]=='-':
                            self.driveMotors(-0.15,0.15)
                            self.move_in_line()
                        elif self.map2analyse[y-1][x]=='-' and self.map2analyse[y+1][x]=='-':
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            currentPoint = (y,x)
                            destinyPoint = self.destinyPointFunc(currentPoint)
                            possible = ['up','right','down']
                            self.path_follow(currentPoint,destinyPoint,possible)
                    elif (self.map2analyse[y-1][x]==' ' and self.map2analyse[y+1][x]==' ' and self.map2analyse[y][x+1]==' ') or self.map2analyse[y][x+1]=='x':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y-1][x] != '-':
                                self.map2analyse[y-1][x] = 'x'
                            if self.map2analyse[y+1][x] != '-':
                                self.map2analyse[y+1][x] = 'x'
                        else:
                            self.driveMotors(-0.15,-0.10)
                    elif self.map2analyse[y-1][x]=='x':
                        self.driveMotors(-0.1,0.1)
                        self.move_in_line()
                    elif self.map2analyse[y+1][x]=='x':
                        self.driveMotors(0.1,-0.1)
                        self.move_in_line()
                    else:
                        self.move_in_line()
                elif (-180 <= self.measures.compass <= -170 or 170 <= self.measures.compass <= 180): #ESQUERDA
                    if self.map2analyse[y-1][x]=='-' and self.map2analyse[y+1][x]=='-' and self.map2analyse[y][x-1]=='-':
                        """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                        currentPoint = (y,x)
                        destinyPoint = self.destinyPointFunc(currentPoint)
                        possible = ['up','left','down']
                        self.path_follow(currentPoint,destinyPoint,possible)
                    elif (self.map2analyse[y-1][x]=='-' or self.map2analyse[y+1][x]=='-') and self.map2analyse[y][x-1]=='x':
                        self.driveMotors(0.10,0.10)
                    elif (self.map2analyse[y-1][x]=='-' or self.map2analyse[y+1][x]=='-') and self.map2analyse[y][x-1]==' ':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y-1][x] != '-':
                                self.map2analyse[y-1][x] = 'x'
                            if self.map2analyse[y+1][x] != '-':
                                self.map2analyse[y+1][x] = 'x'
                        else:
                            if self.map2analyse[y-1][x]=='-' and self.map2analyse[y+1][x]!='-':
                                self.driveMotors(-0.15,0.15)
                                self.move_in_line()
                            elif self.map2analyse[y-1][x]!='-' and self.map2analyse[y+1][x]=='-':
                                self.driveMotors(0.15,-0.15)
                                self.move_in_line()
                            elif self.map2analyse[y-1][x]=='-' and self.map2analyse[y+1][x]=='-':
                                """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                                currentPoint = (y,x)
                                destinyPoint = self.destinyPointFunc(currentPoint)
                                possible = ['up','down']
                                self.path_follow(currentPoint,destinyPoint,possible)
                    elif (self.map2analyse[y-1][x]=='-' or self.map2analyse[y+1][x]=='-') and self.map2analyse[y][x-1]=='-':
                        if self.map2analyse[y-1][x]=='-' and self.map2analyse[y+1][x]!='-':
                            self.driveMotors(-0.15,0.15)
                            self.move_in_line()
                        elif self.map2analyse[y-1][x]!='-' and self.map2analyse[y+1][x]=='-':
                            self.driveMotors(0.15,-0.15)
                            self.move_in_line()
                        elif self.map2analyse[y-1][x]=='-' and self.map2analyse[y+1][x]=='-':
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            currentPoint = (y,x)
                            destinyPoint = self.destinyPointFunc(currentPoint)
                            possible = ['up','left','down']
                            self.path_follow(currentPoint,destinyPoint,possible)
                    elif (self.map2analyse[y-1][x]==' ' and self.map2analyse[y+1][x]==' ' and self.map2analyse[y][x-1]==' ') or self.map2analyse[y][x-1]=='x':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y-1][x] != '-':
                                self.map2analyse[y-1][x] = 'x'
                            if self.map2analyse[y+1][x] != '-':
                                self.map2analyse[y+1][x] = 'x'
                        else:
                            self.driveMotors(-0.15,-0.10)
                    elif self.map2analyse[y-1][x]=='x':
                        self.driveMotors(0.1,-0.1)
                        self.move_in_line()
                    elif self.map2analyse[y+1][x]=='x':
                        self.driveMotors(-0.1,0.1)
                        self.move_in_line()
                    else:
                        self.move_in_line()
                elif (-100 <= self.measures.compass <= -80): #BAIXO
                    if self.map2analyse[y][x-1]=='-' and self.map2analyse[y][x+1]=='-' and self.map2analyse[y+1][x]=='-':
                        """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                        currentPoint = (y,x)
                        destinyPoint = self.destinyPointFunc(currentPoint)
                        possible = ['left','down','right']
                        self.path_follow(currentPoint,destinyPoint,possible)
                        pass
                    elif (self.map2analyse[y][x-1]=='-' or self.map2analyse[y][x+1]=='-') and self.map2analyse[y+1][x]=='x':
                        self.driveMotors(0.10,0.10)
                    elif (self.map2analyse[y][x-1]=='-' or self.map2analyse[y][x+1]=='-') and self.map2analyse[y+1][x]==' ':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y][x-1] != '-':
                                self.map2analyse[y][x-1] = 'x'
                            if self.map2analyse[y][x+1] != '-':
                                self.map2analyse[y][x+1] = 'x'
                        else:
                            if self.map2analyse[y][x-1]=='-' and self.map2analyse[y][x+1]!='-':
                                self.driveMotors(0.15,-0.15)
                                self.move_in_line()
                            elif self.map2analyse[y][x-1]!='-' and self.map2analyse[y][x+1]=='-':
                                self.driveMotors(-0.15,0.15)
                                self.move_in_line()
                            elif self.map2analyse[y][x-1]=='-' and self.map2analyse[y][x+1]=='-':
                                currentPoint = (y,x)
                            destinyPoint = self.destinyPointFunc(currentPoint)
                            possible = ['left','right']
                            self.path_follow(currentPoint,destinyPoint,possible)
                    elif (self.map2analyse[y][x-1]=='-' or self.map2analyse[y][x+1]=='-') and self.map2analyse[y+1][x]=='-':
                        if self.map2analyse[y][x-1]=='-' and self.map2analyse[y][x+1]!='-':
                            self.driveMotors(-0.15,0.15)
                            self.move_in_line()
                        elif self.map2analyse[y][x-1]!='-' and self.map2analyse[y][x+1]=='-':
                            self.driveMotors(0.15,-0.15)
                            self.move_in_line()
                        elif self.map2analyse[y][x-1]=='-' and self.map2analyse[y][x+1]=='-':
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            currentPoint = (y,x)
                            destinyPoint = self.destinyPointFunc(currentPoint)
                            possible = ['left','down','right']
                            self.path_follow(currentPoint,destinyPoint,possible)
                    elif (self.map2analyse[y][x-1]==' ' and self.map2analyse[y][x+1]==' ' and self.map2analyse[y+1][x]==' ') or self.map2analyse[y+1][x]=='x':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y][x-1] != '-':
                                self.map2analyse[y][x-1] = 'x'
                            if self.map2analyse[y][x+1] != '-':
                                self.map2analyse[y][x+1] = 'x'
                        else:
                            self.driveMotors(-0.15,-0.10)
                    elif self.map2analyse[y][x-1]=='x':
                        self.driveMotors(0.1,-0.1)
                        self.move_in_line()
                    elif self.map2analyse[y][x+1]=='x':
                        self.driveMotors(-0.1,0.1)
                        self.move_in_line()
                    else:
                        self.move_in_line()
                elif (80 <= self.measures.compass <= 100): #CIMA
                    if self.map2analyse[y][x-1]=='-' and self.map2analyse[y][x+1]=='-' and self.map2analyse[y-1][x]=='-':
                        """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                        currentPoint = (y,x)
                        destinyPoint = self.destinyPointFunc(currentPoint)
                        possible = ['left','up','right']
                        self.path_follow(currentPoint,destinyPoint,possible)
                    elif (self.map2analyse[y][x-1]=='-' or self.map2analyse[y][x+1]=='-') and self.map2analyse[y-1][x]=='x':
                        self.driveMotors(0.10,0.10)
                    elif (self.map2analyse[y][x-1]=='-' or self.map2analyse[y][x+1]=='-') and self.map2analyse[y-1][x]==' ':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y][x-1] != '-':
                                self.map2analyse[y][x-1] = 'x'
                            if self.map2analyse[y][x+1] != '-':
                                self.map2analyse[y][x+1] = 'x'
                        else:
                            if self.map2analyse[y][x-1]=='-' and self.map2analyse[y][x+1]!='-':
                                self.driveMotors(0.15,-0.15)
                                self.move_in_line()
                            elif self.map2analyse[y][x-1]!='-' and self.map2analyse[y][x+1]=='-':
                                self.driveMotors(-0.15,0.15)
                                self.move_in_line()
                            elif self.map2analyse[y][x-1]=='-' and self.map2analyse[y][x+1]=='-':
                                """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                                currentPoint = (y,x)
                            destinyPoint = self.destinyPointFunc(currentPoint)
                            possible = ['left','right']
                            self.path_follow(currentPoint,destinyPoint,possible)
                    elif (self.map2analyse[y][x-1]=='-' or self.map2analyse[y][x+1]=='-') and self.map2analyse[y-1][x]=='-':
                        if self.map2analyse[y][x-1]=='-' and self.map2analyse[y][x+1]!='-':
                            self.driveMotors(0.15,-0.15)
                            self.move_in_line()
                        elif self.map2analyse[y][x-1]!='-' and self.map2analyse[y][x+1]=='-':
                            self.driveMotors(-0.15,0.15)
                            self.move_in_line()
                        elif self.map2analyse[y][x-1]=='-' and self.map2analyse[y][x+1]=='-':
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            currentPoint = (y,x)
                            destinyPoint = self.destinyPointFunc(currentPoint)
                            possible = ['left','up','right']
                            self.path_follow(currentPoint,destinyPoint,possible)
                    elif (self.map2analyse[y][x-1]==' ' and self.map2analyse[y][x+1]==' ' and self.map2analyse[y-1][x]==' ') or self.map2analyse[y-1][x]=='x':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y][x-1] != '-':
                                self.map2analyse[y][x-1] = 'x'
                            if self.map2analyse[y][x+1] != '-':
                                self.map2analyse[y][x+1] = 'x'
                        else:
                            self.driveMotors(-0.15,-0.10)
                    elif self.map2analyse[y][x-1]=='x':
                        self.driveMotors(-0.1,0.1)
                        self.move_in_line()
                    elif self.map2analyse[y][x+1]=='x':
                        self.driveMotors(0.1,-0.1)
                        self.move_in_line()
                    else:
                        self.move_in_line()
            elif self.measures.lineSensor[0]=='1' and self.measures.lineSensor[1]=='1' and self.measures.lineSensor[2]=='1' and self.measures.lineSensor[3]=='1' and self.measures.lineSensor[4]=='1' and self.measures.lineSensor[5]=='0' and self.measures.lineSensor[6]=='0':
                if (-5 <= self.measures.compass <= 5): #DIREITA
                    if self.map2analyse[y-1][x]=='-':
                        if self.map2analyse[y][x+1]!='-':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                self.driveMotors(0.10,0.10)
                                self.move_in_line()
                        else:
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            currentPoint = (y,x)
                            destinyPoint = self.destinyPointFunc(currentPoint)
                            possible = ['right','up']
                            self.path_follow(currentPoint,destinyPoint,possible)    
                    elif (self.map2analyse[y-1][x]==' ' and self.map2analyse[y][x+1]==' ') or self.map2analyse[y][x+1]=='x':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y-1][x] != '-':
                                self.map2analyse[y-1][x] = 'x'
                        else:
                            self.driveMotors(-0.15,0.15)
                    elif self.map2analyse[y-1][x]=='x':
                        while not (75 <= self.measures.compass <= 105):
                            self.driveMotors(-0.02,0.08)
                            self.readSensors()
                            self.move_in_line()
                    elif self.map2analyse[y-1][x]=='-':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            pass
                        else:
                            self.driveMotors(-0.1,0.1)
                    else:
                        currentPoint = (y,x)
                        destinyPoint = self.destinyPointFunc(currentPoint)
                        possible = ['right','up']
                        self.path_follow(currentPoint,destinyPoint,possible)
                elif (-180 <= self.measures.compass <= -175 or 175 <= self.measures.compass <= 180): #ESQUERDA
                    """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                    if self.map2analyse[y+1][x]=='-':
                        if self.map2analyse[y][x-1]!='-':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                self.driveMotors(0.10,0.10)
                                self.move_in_line()
                        else:
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            currentPoint = (y,x)
                            destinyPoint = self.destinyPointFunc(currentPoint)
                            possible = ['left','down']
                            self.path_follow(currentPoint,destinyPoint,possible)
                    elif (self.map2analyse[y+1][x]==' ' and self.map2analyse[y][x-1]==' ') or self.map2analyse[y][x-1]=='x':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y+1][x] != '-':
                                self.map2analyse[y+1][x] = 'x'
                        else:
                            self.driveMotors(-0.15,0.15)
                    elif self.map2analyse[y+1][x]=='x':
                        while not (-105 <= self.measures.compass <= -75):
                            self.driveMotors(-0.02,0.08)
                            self.readSensors()
                            self.move_in_line()
                    elif self.map2analyse[y+1][x]=='-':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            pass
                        else:
                            self.driveMotors(-0.1,0.1)
                    else:
                        currentPoint = (y,x)
                        destinyPoint = self.destinyPointFunc(currentPoint)
                        possible = ['left','down']
                        self.path_follow(currentPoint,destinyPoint,possible)
                elif (-95 <= self.measures.compass <= -85): #BAIXO
                    """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                    if self.map2analyse[y][x+1]=='-':
                        if self.map2analyse[y+1][x]!='-':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                self.driveMotors(0.10,0.10)
                                self.move_in_line()
                        else:
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            currentPoint = (y,x)
                            destinyPoint = self.destinyPointFunc(currentPoint)
                            possible = ['down','right']
                            self.path_follow(currentPoint,destinyPoint,possible)
                    elif (self.map2analyse[y][x+1]==' ' and self.map2analyse[y+1][x]==' ') or self.map2analyse[y+1][x]=='x':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y][x+1] != '-':
                                self.map2analyse[y][x+1] = 'x'
                        else:
                            self.driveMotors(-0.15,0.15)
                    elif self.map2analyse[y][x+1]=='x':
                        while not (-15 <= self.measures.compass <= 15):
                            self.driveMotors(-0.02,0.08)
                            self.readSensors()
                            self.move_in_line()
                    elif self.map2analyse[y][x+1]=='-':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            pass
                        else:
                            self.driveMotors(-0.1,0.1)
                    else:
                        currentPoint = (y,x)
                        destinyPoint = self.destinyPointFunc(currentPoint)
                        possible = ['down','right']
                        self.path_follow(currentPoint,destinyPoint,possible)
                elif (85 <= self.measures.compass <= 95): #CIMA
                    """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                    if self.map2analyse[y][x-1]=='-':
                        if self.map2analyse[y-1][x]!='-':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                self.driveMotors(0.10,0.10)
                                self.move_in_line()
                        else:
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            currentPoint = (y,x)
                            destinyPoint = self.destinyPointFunc(currentPoint)
                            possible = ['up','left']
                            self.path_follow(currentPoint,destinyPoint,possible)
                    elif (self.map2analyse[y][x-1]==' ' and self.map2analyse[y-1][x]==' ') or self.map2analyse[y-1][x]=='x':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y][x-1] != '-':
                                self.map2analyse[y][x-1] = 'x'
                        else:
                            self.driveMotors(-0.15,0.15)
                    elif self.map2analyse[y][x-1]=='x':
                        while not (-180 <= self.measures.compass <= -165 or 165 <= self.measures.compass <= 180):
                            self.driveMotors(-0.02,0.08)
                            self.readSensors()
                            self.move_in_line()
                    elif self.map2analyse[y][x-1]=='-':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            pass
                        else:
                            self.driveMotors(-0.1,0.1)
                    else:
                        currentPoint = (y,x)
                        destinyPoint = self.destinyPointFunc(currentPoint)
                        possible = ['up','left']
                        self.path_follow(currentPoint,destinyPoint,possible)
            elif self.measures.lineSensor[0]=='0' and self.measures.lineSensor[1]=='0' and self.measures.lineSensor[2]=='1' and self.measures.lineSensor[3]=='1' and self.measures.lineSensor[4]=='1' and self.measures.lineSensor[5]=='1' and self.measures.lineSensor[6]=='1':
                if (-5 <= self.measures.compass <= 5): #DIREITA
                    """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                    if self.map2analyse[y+1][x]=='-':
                        if self.map2analyse[y][x+1]!='-':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                self.driveMotors(0.10,0.10)
                                self.move_in_line()
                        else:
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            currentPoint = (y,x)
                            destinyPoint = self.destinyPointFunc(currentPoint)
                            possible = ['right','down']
                            self.path_follow(currentPoint,destinyPoint,possible)
                    elif (self.map2analyse[y+1][x]==' ' and self.map2analyse[y][x+1]==' ') or self.map2analyse[y][x+1]=='x':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y+1][x] != '-':
                                self.map2analyse[y+1][x] = 'x'
                        else:
                            self.driveMotors(0.15,-0.15)
                    elif self.map2analyse[y+1][x]=='x':
                        while not (-105 <= self.measures.compass <= -75):
                            self.driveMotors(0.08,-0.02)
                            self.readSensors()
                            self.move_in_line()
                    elif self.map2analyse[y+1][x]=='-':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            pass
                        else:
                            self.driveMotors(0.1,-0.1)
                    else:
                        currentPoint = (y,x)
                        destinyPoint = self.destinyPointFunc(currentPoint)
                        possible = ['right','down']
                        self.path_follow(currentPoint,destinyPoint,possible)
                elif (-180 <= self.measures.compass <= -175 or 175 <= self.measures.compass <= 180): #ESQUERDA
                    """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                    if self.map2analyse[y-1][x]=='-':
                        if self.map2analyse[y][x-1]!='-':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                self.driveMotors(0.10,0.10)
                                self.move_in_line()
                        else:
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            currentPoint = (y,x)
                            destinyPoint = self.destinyPointFunc(currentPoint)
                            possible = ['left','up']
                            self.path_follow(currentPoint,destinyPoint,possible)
                    elif (self.map2analyse[y-1][x]==' ' and self.map2analyse[y][x-1]==' ') or self.map2analyse[y][x-1]=='x':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y-1][x] != '-':
                                self.map2analyse[y-1][x] = 'x'
                        else:
                            self.driveMotors(0.15,-0.15)
                    elif self.map2analyse[y-1][x]=='x':
                        while not (75 <= self.measures.compass <= 105):
                            self.driveMotors(0.08,-0.02)
                            self.readSensors()
                            self.move_in_line()
                    elif self.map2analyse[y-1][x]=='-':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            pass
                        else:
                            self.driveMotors(0.1,-0.1)
                    else:
                        currentPoint = (y,x)
                        destinyPoint = self.destinyPointFunc(currentPoint)
                        possible = ['left','up']
                        self.path_follow(currentPoint,destinyPoint,possible)
                elif (-95 <= self.measures.compass <= -85): #BAIXO
                    """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                    if self.map2analyse[y][x-1]=='-':
                        if self.map2analyse[y+1][x]!='-':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                self.driveMotors(0.10,0.10)
                                self.move_in_line()
                        else:
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            currentPoint = (y,x)
                            destinyPoint = self.destinyPointFunc(currentPoint)
                            possible = ['down','left']
                            self.path_follow(currentPoint,destinyPoint,possible)
                    elif (self.map2analyse[y][x-1]==' ' and self.map2analyse[y+1][x]==' ') or self.map2analyse[y+1][x]=='x':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y][x-1] != '-':
                                self.map2analyse[y][x-1] = 'x'
                        else:
                            self.driveMotors(0.15,-0.15)
                    elif self.map2analyse[y][x-1]=='x':
                        while not (-180 <= self.measures.compass <= -165 or 165 <= self.measures.compass <= 180):
                            self.driveMotors(0.08,-0.02)
                            self.readSensors()
                            self.move_in_line()
                    elif self.map2analyse[y][x-1]=='-':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            pass
                        else:
                            self.driveMotors(0.1,-0.1)
                    else:
                        currentPoint = (y,x)
                        destinyPoint = self.destinyPointFunc(currentPoint)
                        possible = ['down','left']
                        self.path_follow(currentPoint,destinyPoint,possible)
                elif (85 <= self.measures.compass <= 95): #CIMA
                    """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                    if self.map2analyse[y][x+1]=='-':
                        if self.map2analyse[y-1][x]!='-':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                self.driveMotors(0.10,0.10)
                                self.move_in_line()
                        else:
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            currentPoint = (y,x)
                            destinyPoint = self.destinyPointFunc(currentPoint)
                            possible = ['up','right']
                            self.path_follow(currentPoint,destinyPoint,possible)
                    elif (self.map2analyse[y][x+1]==' ' and self.map2analyse[y-1][x]==' ') or self.map2analyse[y-1][x]=='x':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            if self.map2analyse[y][x+1] != '-':
                                self.map2analyse[y][x+1] = 'x'
                        else:
                            self.driveMotors(0.15,-0.15)
                    elif self.map2analyse[y][x+1]=='x':
                        while not (-15 <= self.measures.compass <= 15):
                            self.driveMotors(0.08,-0.02)
                            self.readSensors()
                            self.move_in_line()
                    elif self.map2analyse[y][x+1]=='-':
                        self.driveMotors(0.10,0.10)
                        self.readSensors()
                        if self.measures.lineSensor[3]=='1':
                            pass
                        else:
                            self.driveMotors(0.1,-0.1)
                    else:
                        currentPoint = (y,x)
                        destinyPoint = self.destinyPointFunc(currentPoint)
                        possible = ['up','right']
                        self.path_follow(currentPoint,destinyPoint,possible)
            else:
                self.move_in_line()
            if self.previousPoint!=(y,x):
                self.previousPoint = (y,x)

    def destinyPointFunc(self,currentPoint):
        points2analyse = []
        for y in range(21):
            for x in range(49):
                if self.map2analyse[y][x]=='x':
                    print(f"PONTO - ({y},{x}) - {self.map2analyse[y][x]}")
                    count = 0
                    if (self.map2analyse[y][x+1]=='-' and self.map2analyse[y+1][x]=='-') or (self.map2analyse[y][x+1]=='-' and self.map2analyse[y-1][x]=='-') or (self.map2analyse[y][x-1]=='-' and self.map2analyse[y+1][x]=='-') or (self.map2analyse[y][x-1]=='-' and self.map2analyse[y-1][x]=='-'):
                        count = 1
                    print(f"COUNT = {count}")
                    if count<1:
                        points2analyse.append((y,x))
        min_distance = 100000000000000
        destiny_point = 0
        if len(points2analyse)==0:
            self.finish()
            self.playGame = False
        for point in points2analyse:
            dist = ((point[0]-currentPoint[0])**2 + (point[1]-currentPoint[1])**2)
            if dist < min_distance:
                min_distance = dist
                destiny_point = point
        #if destiny_point == 0:
        #    return (self.MidY,self.MidX)
        print(f"DESTINYpoint - {destiny_point}\n")
        if destiny_point==0:
            self.finish()
            self.playGame = False
        return destiny_point
        
    def path_follow(self,currentPoint,destinyPoint,possible):
        
        direction = ""
        min_dist = 100000000000000
        directions = []
        print(f"POSSIBLE - {possible}\n")
        for i in possible:
            if destinyPoint==int(0):
                self.finish()
                self.playGame = False
                break
            print(type(destinyPoint))
            if i=='up':
                print("--------")
                print(destinyPoint)
                print(destinyPoint)
                point = (currentPoint[0]-1,currentPoint[1])
                dist = ((destinyPoint[0]-point[0])**2 + (destinyPoint[1]-point[1])**2)
                if dist<=min_dist and point!=self.previousPoint:
                    min_dist = dist
                    directions.append('up')
            elif i=='right':
                point = (currentPoint[0],currentPoint[1]+1)
                dist = (destinyPoint[0]-point[0])**2 + (destinyPoint[1]-point[1])**2
                if dist<=min_dist and point!=self.previousPoint:
                    min_dist = dist
                    directions.append('right')
            elif i=='down':
                point = (currentPoint[0]+1,currentPoint[1])
                dist = (destinyPoint[0]-point[0])**2 + (destinyPoint[1]-point[1])**2
                if dist<=min_dist and point!=self.previousPoint:
                    min_dist = dist
                    directions.append('down')
            elif i=='left':
                point = (currentPoint[0],currentPoint[1]-1)
                dist = (destinyPoint[0]-point[0])**2 + (destinyPoint[1]-point[1])**2
                if dist<=min_dist and point!=self.previousPoint:
                    min_dist = dist
                    directions.append('left')
            print(f"CURRENT POINT {currentPoint} - DESTINYPOINT {destinyPoint} - dist {dist}")
        if len(directions)==1:
            direction = directions[0]
        elif len(directions)>1:
            direction = random.choice(directions)
        if direction=='up':
            while not (80 <= self.measures.compass <= 100):
                print(f"COMPASS - {self.measures.compass}")
                if (-180 <= self.measures.compass <= -170) or (100 <= self.measures.compass <= 180):
                    self.driveMotors(0.05,-0.02)
                elif (-10 <= self.measures.compass <=80):
                    self.driveMotors(-0.02,0.05)
                self.readSensors()
                if self.measures.lineSensor[3]=='1':
                    self.driveMotors(0.1,0.1)
                else:
                    self.driveMotors(-0.05,-0.05)
            # self.driveMotors(0.1,0.1)
        elif direction=='right':
            while not (-10 <= self.measures.compass <= 10):
                if (10 <= self.measures.compass <= 100):
                    self.driveMotors(0.05,-0.02)
                elif (-100 <= self.measures.compass <=-10):
                    self.driveMotors(-0.02,0.05)
                self.readSensors()
                if self.measures.lineSensor[3]=='1':
                    self.driveMotors(0.1,0.1)
                else:
                    self.driveMotors(-0.05,-0.05)
            #self.driveMotors(0.1,0.1)
        elif direction=='down':
            while not (-100 <= self.measures.compass <= -80):
                if (-80 <= self.measures.compass <= 10):
                    self.driveMotors(0.05,-0.02)
                elif (-180 <= self.measures.compass <=-100) or (170 <= self.measures.compass <= 180):
                    self.driveMotors(-0.02,0.05)
                self.readSensors()
                if self.measures.lineSensor[3]=='1':
                    self.driveMotors(0.1,0.1)
                else:
                    self.driveMotors(-0.05,-0.05)
            #self.driveMotors(0.1,0.1)
        elif direction=='left':
            while not (-180 <= self.measures.compass <= -170 or 170 <= self.measures.compass <= 180):
                if (-170 <= self.measures.compass <= -80):
                    self.driveMotors(0.05,-0.02)
                elif (80 <= self.measures.compass <=170):
                    self.driveMotors(-0.02,0.05)
                self.readSensors()
                if self.measures.lineSensor[3]=='1':
                    self.driveMotors(0.1,0.1)
                else:
                    self.driveMotors(-0.05,-0.05)
            #self.driveMotors(0.1,0.1)
        print(f"DIRECTION - {direction}\n")

        


                        
                

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
            self.readSensors()
            if self.measures.lineSensor[0]=='0' and self.measures.lineSensor[1]=='0' and self.measures.lineSensor[2]=='1' and self.measures.lineSensor[3]=='1' and self.measures.lineSensor[4]=='1' and self.measures.lineSensor[5]=='0' and self.measures.lineSensor[6]=='0':
                if (-5 <= self.measures.compass <= 5): #DIREITA
                    while not (-180 <= self.measures.compass <= -175 or 175 <= self.measures.compass <= 180):
                        self.driveMotors(-0.05,0.05)
                        self.readSensors()
                    self.move_in_line()
                elif (-180 <= self.measures.compass <= -175 or 175 <= self.measures.compass <= 180): #ESQUERDA
                    while not (-5 <= self.measures.compass <= 5):
                        self.driveMotors(-0.05,0.05)
                        self.readSensors()
                    self.move_in_line()
                elif (-95 <= self.measures.compass <= -85): #BAIXO
                    while not (85 <= self.measures.compass <= 95):
                        self.driveMotors(-0.05,0.05)
                        self.readSensors()
                    self.move_in_line()
                elif (85 <= self.measures.compass <= 95): #CIMA
                    while not (-95 <= self.measures.compass <= -85):
                        self.driveMotors(-0.05,0.05)
                        self.readSensors()
                    self.move_in_line()
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

    elif (sys.argv[i] == "--file" or sys.argv[i] == "-f") and i != len(sys.argv) - 1:
        file = sys.argv[i + 1]
    else:
        print("Unkown argument", sys.argv[i])
        quit()

if __name__ == '__main__':
    rob=MyRob(rob_name,pos,[0.0,60.0,-60.0,180.0],host,file)
    if mapc != None:
        rob.setMap(mapc.labMap)
        rob.printMap()
    
    rob.run()
