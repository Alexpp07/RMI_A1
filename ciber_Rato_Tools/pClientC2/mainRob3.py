
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
    def __init__(self, rob_name, rob_id, angles, host, filename):
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

        self.traceMap = []
        self.setMap(self.traceMap)
        print("hello")
        self.printMap()

        self.beacon_maze = []

        for x in range(21):
            minimap = []
            for y in range(49):
                minimap.append(' ')
            self.traceMap.append(minimap)
            self.setMap(self.traceMap)

        for x in range(21):
            mini = []
            for y in range(49):
                mini.append('0')
            self.beacon_maze.append(mini)

        self.posInitialX = ''
        self.posInitialX2 = ''
        self.posInitialY2 = ''
        self.posInitialY = ''
        self.prevPosX = ''
        self.prevPosY = ''
        count = 0
        self.firstTime = True
        self.previousPoint = (0,0)
        self.playGame = True
        self.beacon_coords = []
        self.countBeacons = 0

        while self.playGame:
            f = open(self.filename, 'w')
            file2 = open("mini.txt", 'w')

            self.readSensors()

            if self.posInitialX=='' and self.posInitialY=='':
                self.posInitialX = self.measures.x
                self.posInitialY = self.measures.y

            if self.prevPosX=='' and self.prevPosY=='':
                self.prevPosX = self.measures.x
                self.prevPosY = self.measures.y

            posMidX = 24
            posMidY = 10

            self.MidX = 24
            self.MidY = 10

            difX = self.posInitialX - self.measures.x
            difY = self.posInitialY - self.measures.y

            x = int(posMidX) - int(round(difX,0))
            y = int(posMidY) + int(round(difY,0))

            self.posInitialX2 = x
            self.posInitialY2 = y

            self.currentPoint = (y,x)

            if self.measures.ground!=-1:
                if [x,y] not in self.beacon_coords:
                    self.beacon_coords.append([x,y])
                    print(self.beacon_coords)
                    print(self.nBeacons)
                self.traceMap[y][x] = 'O'
    
            self.beacon_maze[y][x] = '1'

            if len(self.beacon_coords)==self.nBeacons:
                if -5 <= self.measures.compass <= 5: #DIREITA
                    if self.traceMap[y][x]==' ' and (self.traceMap[y][x-1]==' ' or self.traceMap[y][x-1]=='I') and (self.traceMap[y][x+1]==' ' or self.traceMap[y][x+1]=='I') and (self.traceMap[y-1][x]==' ' or self.traceMap[y-1][x]=='I') and (self.traceMap[y+1][x]==' ' or self.traceMap[y+1][x]=='I'):
                        self.traceMap[y][x] = '-'
                elif -95 <= self.measures.compass <= -85: #BAIXO
                    if self.traceMap[y][x]==' ' and (self.traceMap[y][x-1]==' ' or self.traceMap[y][x-1]=='I') and (self.traceMap[y][x+1]==' ' or self.traceMap[y][x+1]=='I') and (self.traceMap[y-1][x]==' ' or self.traceMap[y-1][x]=='I') and (self.traceMap[y+1][x]==' ' or self.traceMap[y+1][x]=='I'):
                        self.traceMap[y][x] = '|'
                elif -180 <= self.measures.compass <= -175 or 175 <= self.measures.compass <= 180: #ESQUERDA
                    if self.traceMap[y][x]==' ' and (self.traceMap[y][x-1]==' ' or self.traceMap[y][x-1]=='I') and (self.traceMap[y][x+1]==' ' or self.traceMap[y][x+1]=='I') and (self.traceMap[y-1][x]==' ' or self.traceMap[y-1][x]=='I') and (self.traceMap[y+1][x]==' ' or self.traceMap[y+1][x]=='I'):
                        self.traceMap[y][x] = '-'
                elif 85 <= self.measures.compass <= 95: #CIMA
                    if self.traceMap[y][x]==' ' and (self.traceMap[y][x-1]==' ' or self.traceMap[y][x-1]=='I') and (self.traceMap[y][x+1]==' ' or self.traceMap[y][x+1]=='I') and (self.traceMap[y-1][x]==' ' or self.traceMap[y-1][x]=='I') and (self.traceMap[y+1][x]==' ' or self.traceMap[y+1][x]=='I'):
                        self.traceMap[y][x] = '|'

            # print(allMap)
            self.setMap(self.traceMap)

            for x in range(21):
                for y in range(49):
                    f.write(self.traceMap[x][y])
                f.write('\n')

            f.close

            for x in range(21):
                for y in range(49):
                    file2.write(self.beacon_maze[x][y])
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
                self.wander(self.traceMap,self.posInitialX,self.posInitialY,count)
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
                self.wander(self.traceMap,self.posInitialX,self.posInitialY,count)
            

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

            if self.measures.ground!=-1:
                if [x,y] not in self.beacon_coords:
                    self.beacon_coords.append([x,y])

            print(self.measures.lineSensor)

            if len(self.beacon_coords) == int(self.nBeacons):
                "FUNÇÃO UTILIZADA APÓS SABERMOS ONDE ESTÃO TODOS OS BEACONS"
                print("ACABOU")
                self.found_all_beacons(24,10)
            else:
                if self.measures.lineSensor[0]=='1' and self.measures.lineSensor[1]=='1' and self.measures.lineSensor[2]=='1' and self.measures.lineSensor[3]=='1' and self.measures.lineSensor[4]=='1' and self.measures.lineSensor[5]=='1' and self.measures.lineSensor[6]=='1':
                    if (-10 <= self.measures.compass <= 10): #DIREITA
                        if self.beacon_maze[y-1][x]=='1' or self.beacon_maze[y+1][x]=='1' and self.beacon_maze[y][x+1]=='1':
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            currentPoint = (y,x)
                            destinyPoint = self.destinyPointFunc(currentPoint)
                            possible = ['up','right','down']
                            self.path_follow(currentPoint,destinyPoint,possible)
                        elif (self.beacon_maze[y-1][x]=='1' or self.beacon_maze[y+1][x]=='1') and self.beacon_maze[y][x+1]=='x':
                            self.driveMotors(0.10,0.10)
                        elif (self.beacon_maze[y-1][x]=='1' or self.beacon_maze[y+1][x]=='1') and self.beacon_maze[y][x+1]=='0':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                if self.beacon_maze[y-1][x] != '1':
                                    self.beacon_maze[y-1][x] = 'x'
                                if self.beacon_maze[y+1][x] != '1':
                                    self.beacon_maze[y+1][x] = 'x'
                            else:
                                if self.beacon_maze[y-1][x]=='1' and self.beacon_maze[y+1][x]!='1':
                                    self.driveMotors(0.15,-0.15)
                                    self.move_in_line()
                                elif self.beacon_maze[y-1][x]!='1' and self.beacon_maze[y+1][x]=='1':
                                    self.driveMotors(-0.15,0.15)
                                    self.move_in_line()
                                elif self.beacon_maze[y-1][x]=='1' and self.beacon_maze[y+1][x]=='1':
                                    """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                                    currentPoint = (y,x)
                                    destinyPoint = self.destinyPointFunc(currentPoint)
                                    possible = ['up','down']
                                    self.path_follow(currentPoint,destinyPoint,possible)
                        elif (self.beacon_maze[y-1][x]=='1' or self.beacon_maze[y+1][x]=='1') and self.beacon_maze[y][x+1]=='1':
                            if self.beacon_maze[y-1][x]=='1' and self.beacon_maze[y+1][x]!='1':
                                self.driveMotors(0.15,-0.15)
                                self.move_in_line()
                            elif self.beacon_maze[y-1][x]!='1' and self.beacon_maze[y+1][x]=='1':
                                self.driveMotors(-0.15,0.15)
                                self.move_in_line()
                            elif self.beacon_maze[y-1][x]=='1' and self.beacon_maze[y+1][x]=='1':
                                """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                                currentPoint = (y,x)
                                destinyPoint = self.destinyPointFunc(currentPoint)
                                possible = ['up','right','down']
                                self.path_follow(currentPoint,destinyPoint,possible)
                        elif (self.beacon_maze[y-1][x]=='0' and self.beacon_maze[y+1][x]=='0' and self.beacon_maze[y][x+1]=='0') or self.beacon_maze[y][x+1]=='x':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                if self.beacon_maze[y-1][x] != '1':
                                    self.beacon_maze[y-1][x] = 'x'
                                if self.beacon_maze[y+1][x] != '1':
                                    self.beacon_maze[y+1][x] = 'x'
                            else:
                                self.move_in_line()
                        elif self.beacon_maze[y-1][x]=='x':
                            self.driveMotors(-0.1,0.1)
                            self.move_in_line()
                        elif self.beacon_maze[y+1][x]=='x':
                            self.driveMotors(0.1,-0.1)
                            self.move_in_line()
                        else:
                            self.move_in_line()
                    elif (-180 <= self.measures.compass <= -170 or 170 <= self.measures.compass <= 180): #ESQUERDA
                        if self.beacon_maze[y-1][x]=='1' and self.beacon_maze[y+1][x]=='1' and self.beacon_maze[y][x-1]=='1':
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            currentPoint = (y,x)
                            destinyPoint = self.destinyPointFunc(currentPoint)
                            possible = ['up','left','down']
                            self.path_follow(currentPoint,destinyPoint,possible)
                        elif (self.beacon_maze[y-1][x]=='1' or self.beacon_maze[y+1][x]=='1') and self.beacon_maze[y][x-1]=='x':
                            self.driveMotors(0.10,0.10)
                        elif (self.beacon_maze[y-1][x]=='1' or self.beacon_maze[y+1][x]=='1') and self.beacon_maze[y][x-1]=='0':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                if self.beacon_maze[y-1][x] != '1':
                                    self.beacon_maze[y-1][x] = 'x'
                                if self.beacon_maze[y+1][x] != '1':
                                    self.beacon_maze[y+1][x] = 'x'
                            else:
                                if self.beacon_maze[y-1][x]=='1' and self.beacon_maze[y+1][x]!='1':
                                    self.driveMotors(-0.15,0.15)
                                    self.move_in_line()
                                elif self.beacon_maze[y-1][x]!='1' and self.beacon_maze[y+1][x]=='1':
                                    self.driveMotors(0.15,-0.15)
                                    self.move_in_line()
                                elif self.beacon_maze[y-1][x]=='1' and self.beacon_maze[y+1][x]=='1':
                                    """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                                    currentPoint = (y,x)
                                    destinyPoint = self.destinyPointFunc(currentPoint)
                                    possible = ['up','down']
                                    self.path_follow(currentPoint,destinyPoint,possible)
                        elif (self.beacon_maze[y-1][x]=='1' or self.beacon_maze[y+1][x]=='1') and self.beacon_maze[y][x-1]=='1':
                            if self.beacon_maze[y-1][x]=='1' and self.beacon_maze[y+1][x]!='1':
                                self.driveMotors(-0.15,0.15)
                                self.move_in_line()
                            elif self.beacon_maze[y-1][x]!='1' and self.beacon_maze[y+1][x]=='1':
                                self.driveMotors(0.15,-0.15)
                                self.move_in_line()
                            elif self.beacon_maze[y-1][x]=='1' and self.beacon_maze[y+1][x]=='1':
                                """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                                currentPoint = (y,x)
                                destinyPoint = self.destinyPointFunc(currentPoint)
                                possible = ['up','left','down']
                                self.path_follow(currentPoint,destinyPoint,possible)
                        elif (self.beacon_maze[y-1][x]=='0' and self.beacon_maze[y+1][x]=='0' and self.beacon_maze[y][x-1]=='0') or self.beacon_maze[y][x-1]=='x':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                if self.beacon_maze[y-1][x] != '1':
                                    self.beacon_maze[y-1][x] = 'x'
                                if self.beacon_maze[y+1][x] != '1':
                                    self.beacon_maze[y+1][x] = 'x'
                            else:
                                self.driveMotors(-0.15,-0.10)
                        elif self.beacon_maze[y-1][x]=='x':
                            self.driveMotors(0.1,-0.1)
                            self.move_in_line()
                        elif self.beacon_maze[y+1][x]=='x':
                            self.driveMotors(-0.1,0.1)
                            self.move_in_line()
                        else:
                            self.move_in_line()
                    elif (-100 <= self.measures.compass <= -80): #BAIXO
                        if self.beacon_maze[y][x-1]=='1' and self.beacon_maze[y][x+1]=='1' and self.beacon_maze[y+1][x]=='1':
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            currentPoint = (y,x)
                            destinyPoint = self.destinyPointFunc(currentPoint)
                            possible = ['left','down','right']
                            self.path_follow(currentPoint,destinyPoint,possible)
                            pass
                        elif (self.beacon_maze[y][x-1]=='1' or self.beacon_maze[y][x+1]=='1') and self.beacon_maze[y+1][x]=='x':
                            self.driveMotors(0.10,0.10)
                        elif (self.beacon_maze[y][x-1]=='1' or self.beacon_maze[y][x+1]=='1') and self.beacon_maze[y+1][x]=='0':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                if self.beacon_maze[y][x-1] != '1':
                                    self.beacon_maze[y][x-1] = 'x'
                                if self.beacon_maze[y][x+1] != '1':
                                    self.beacon_maze[y][x+1] = 'x'
                            else:
                                if self.beacon_maze[y][x-1]=='1' and self.beacon_maze[y][x+1]!='1':
                                    self.driveMotors(0.15,-0.15)
                                    self.move_in_line()
                                elif self.beacon_maze[y][x-1]!='1' and self.beacon_maze[y][x+1]=='1':
                                    self.driveMotors(-0.15,0.15)
                                    self.move_in_line()
                                elif self.beacon_maze[y][x-1]=='1' and self.beacon_maze[y][x+1]=='1':
                                    currentPoint = (y,x)
                                destinyPoint = self.destinyPointFunc(currentPoint)
                                possible = ['left','right']
                                self.path_follow(currentPoint,destinyPoint,possible)
                        elif (self.beacon_maze[y][x-1]=='1' or self.beacon_maze[y][x+1]=='1') and self.beacon_maze[y+1][x]=='1':
                            if self.beacon_maze[y][x-1]=='1' and self.beacon_maze[y][x+1]!='1':
                                self.driveMotors(-0.15,0.15)
                                self.move_in_line()
                            elif self.beacon_maze[y][x-1]!='1' and self.beacon_maze[y][x+1]=='1':
                                self.driveMotors(0.15,-0.15)
                                self.move_in_line()
                            elif self.beacon_maze[y][x-1]=='1' and self.beacon_maze[y][x+1]=='1':
                                """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                                currentPoint = (y,x)
                                destinyPoint = self.destinyPointFunc(currentPoint)
                                possible = ['left','down','right']
                                self.path_follow(currentPoint,destinyPoint,possible)
                        elif (self.beacon_maze[y][x-1]=='0' and self.beacon_maze[y][x+1]=='0' and self.beacon_maze[y+1][x]=='0') or self.beacon_maze[y+1][x]=='x':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                if self.beacon_maze[y][x-1] != '1':
                                    self.beacon_maze[y][x-1] = 'x'
                                if self.beacon_maze[y][x+1] != '1':
                                    self.beacon_maze[y][x+1] = 'x'
                            else:
                                self.driveMotors(-0.15,-0.10)
                        elif self.beacon_maze[y][x-1]=='x':
                            self.driveMotors(0.1,-0.1)
                            self.move_in_line()
                        elif self.beacon_maze[y][x+1]=='x':
                            self.driveMotors(-0.1,0.1)
                            self.move_in_line()
                        else:
                            self.move_in_line()
                    elif (80 <= self.measures.compass <= 100): #CIMA
                        if self.beacon_maze[y][x-1]=='1' and self.beacon_maze[y][x+1]=='1' and self.beacon_maze[y-1][x]=='1':
                            """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                            currentPoint = (y,x)
                            destinyPoint = self.destinyPointFunc(currentPoint)
                            possible = ['left','up','right']
                            self.path_follow(currentPoint,destinyPoint,possible)
                        elif (self.beacon_maze[y][x-1]=='1' or self.beacon_maze[y][x+1]=='1') and self.beacon_maze[y-1][x]=='x':
                            self.driveMotors(0.10,0.10)
                        elif (self.beacon_maze[y][x-1]=='1' or self.beacon_maze[y][x+1]=='1') and self.beacon_maze[y-1][x]=='0':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                if self.beacon_maze[y][x-1] != '1':
                                    self.beacon_maze[y][x-1] = 'x'
                                if self.beacon_maze[y][x+1] != '1':
                                    self.beacon_maze[y][x+1] = 'x'
                            else:
                                if self.beacon_maze[y][x-1]=='1' and self.beacon_maze[y][x+1]!='1':
                                    self.driveMotors(0.15,-0.15)
                                    self.move_in_line()
                                elif self.beacon_maze[y][x-1]!='1' and self.beacon_maze[y][x+1]=='1':
                                    self.driveMotors(-0.15,0.15)
                                    self.move_in_line()
                                elif self.beacon_maze[y][x-1]=='1' and self.beacon_maze[y][x+1]=='1':
                                    """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                                    currentPoint = (y,x)
                                destinyPoint = self.destinyPointFunc(currentPoint)
                                possible = ['left','right']
                                self.path_follow(currentPoint,destinyPoint,possible)
                        elif (self.beacon_maze[y][x-1]=='1' or self.beacon_maze[y][x+1]=='1') and self.beacon_maze[y-1][x]=='1':
                            if self.beacon_maze[y][x-1]=='1' and self.beacon_maze[y][x+1]!='1':
                                self.driveMotors(0.15,-0.15)
                                self.move_in_line()
                            elif self.beacon_maze[y][x-1]!='1' and self.beacon_maze[y][x+1]=='1':
                                self.driveMotors(-0.15,0.15)
                                self.move_in_line()
                            elif self.beacon_maze[y][x-1]=='1' and self.beacon_maze[y][x+1]=='1':
                                """ACRESCENTAR CONDIÇÃO PARA PROCURAR OS CAMINHOS X MAIS PROXIMOS"""
                                currentPoint = (y,x)
                                destinyPoint = self.destinyPointFunc(currentPoint)
                                possible = ['left','up','right']
                                self.path_follow(currentPoint,destinyPoint,possible)
                        elif (self.beacon_maze[y][x-1]=='0' and self.beacon_maze[y][x+1]=='0' and self.beacon_maze[y-1][x]=='0') or self.beacon_maze[y-1][x]=='x':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                if self.beacon_maze[y][x-1] != '1':
                                    self.beacon_maze[y][x-1] = 'x'
                                if self.beacon_maze[y][x+1] != '1':
                                    self.beacon_maze[y][x+1] = 'x'
                            else:
                                self.driveMotors(-0.15,-0.10)
                        elif self.beacon_maze[y][x-1]=='x':
                            self.driveMotors(-0.1,0.1)
                            self.move_in_line()
                        elif self.beacon_maze[y][x+1]=='x':
                            self.driveMotors(0.1,-0.1)
                            self.move_in_line()
                        else:
                            self.move_in_line()
                elif self.measures.lineSensor[0]=='1' and self.measures.lineSensor[1]=='1' and self.measures.lineSensor[2]=='1' and self.measures.lineSensor[3]=='1' and self.measures.lineSensor[4]=='1' and self.measures.lineSensor[5]=='0' and self.measures.lineSensor[6]=='0':
                    if (-5 <= self.measures.compass <= 5): #DIREITA
                        if self.beacon_maze[y-1][x]=='1':
                            if self.beacon_maze[y][x+1]!='1':
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
                        elif (self.beacon_maze[y-1][x]=='0' and self.beacon_maze[y][x+1]=='0') or self.beacon_maze[y][x+1]=='x':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                if self.beacon_maze[y-1][x] != '1':
                                    self.beacon_maze[y-1][x] = 'x'
                            else:
                                self.driveMotors(-0.15,0.15)
                        elif self.beacon_maze[y-1][x]=='x':
                            while not (75 <= self.measures.compass <= 105):
                                self.driveMotors(-0.02,0.08)
                                self.readSensors()
                                self.move_in_line()
                        elif self.beacon_maze[y-1][x]=='1':
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
                        if self.beacon_maze[y+1][x]=='1':
                            if self.beacon_maze[y][x-1]!='1':
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
                        elif (self.beacon_maze[y+1][x]=='0' and self.beacon_maze[y][x-1]=='0') or self.beacon_maze[y][x-1]=='x':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                if self.beacon_maze[y+1][x] != '1':
                                    self.beacon_maze[y+1][x] = 'x'
                            else:
                                self.driveMotors(-0.15,0.15)
                        elif self.beacon_maze[y+1][x]=='x':
                            while not (-105 <= self.measures.compass <= -75):
                                self.driveMotors(-0.02,0.08)
                                self.readSensors()
                                self.move_in_line()
                        elif self.beacon_maze[y+1][x]=='1':
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
                        if self.beacon_maze[y][x+1]=='1':
                            if self.beacon_maze[y+1][x]!='1':
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
                        elif (self.beacon_maze[y][x+1]=='0' and self.beacon_maze[y+1][x]=='0') or self.beacon_maze[y+1][x]=='x':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                if self.beacon_maze[y][x+1] != '1':
                                    self.beacon_maze[y][x+1] = 'x'
                            else:
                                self.driveMotors(-0.15,0.15)
                        elif self.beacon_maze[y][x+1]=='x':
                            while not (-15 <= self.measures.compass <= 15):
                                self.driveMotors(-0.02,0.08)
                                self.readSensors()
                                self.move_in_line()
                        elif self.beacon_maze[y][x+1]=='1':
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
                        if self.beacon_maze[y][x-1]=='1':
                            if self.beacon_maze[y-1][x]!='1':
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
                        elif (self.beacon_maze[y][x-1]=='0' and self.beacon_maze[y-1][x]=='0') or self.beacon_maze[y-1][x]=='x':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                if self.beacon_maze[y][x-1] != '1':
                                    self.beacon_maze[y][x-1] = 'x'
                            else:
                                self.driveMotors(-0.15,0.15)
                        elif self.beacon_maze[y][x-1]=='x':
                            while not (-180 <= self.measures.compass <= -165 or 165 <= self.measures.compass <= 180):
                                self.driveMotors(-0.02,0.08)
                                self.readSensors()
                                self.move_in_line()
                        elif self.beacon_maze[y][x-1]=='1':
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
                        if self.beacon_maze[y+1][x]=='1':
                            if self.beacon_maze[y][x+1]!='1':
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
                        elif (self.beacon_maze[y+1][x]=='0' and self.beacon_maze[y][x+1]=='0') or self.beacon_maze[y][x+1]=='x':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                if self.beacon_maze[y+1][x] != '1':
                                    self.beacon_maze[y+1][x] = 'x'
                            else:
                                self.driveMotors(0.15,-0.15)
                        elif self.beacon_maze[y+1][x]=='x':
                            while not (-105 <= self.measures.compass <= -75):
                                self.driveMotors(0.08,-0.02)
                                self.readSensors()
                                self.move_in_line()
                        elif self.beacon_maze[y+1][x]=='1':
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
                        if self.beacon_maze[y-1][x]=='1':
                            if self.beacon_maze[y][x-1]!='1':
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
                        elif (self.beacon_maze[y-1][x]=='0' and self.beacon_maze[y][x-1]=='0') or self.beacon_maze[y][x-1]=='x':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                if self.beacon_maze[y-1][x] != '1':
                                    self.beacon_maze[y-1][x] = 'x'
                            else:
                                self.driveMotors(0.15,-0.15)
                        elif self.beacon_maze[y-1][x]=='x':
                            while not (75 <= self.measures.compass <= 105):
                                self.driveMotors(0.08,-0.02)
                                self.readSensors()
                                self.move_in_line()
                        elif self.beacon_maze[y-1][x]=='1':
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
                        if self.beacon_maze[y][x-1]=='1':
                            if self.beacon_maze[y+1][x]!='1':
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
                        elif (self.beacon_maze[y][x-1]=='0' and self.beacon_maze[y+1][x]=='0') or self.beacon_maze[y+1][x]=='x':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                if self.beacon_maze[y][x-1] != '1':
                                    self.beacon_maze[y][x-1] = 'x'
                            else:
                                self.driveMotors(0.15,-0.15)
                        elif self.beacon_maze[y][x-1]=='x':
                            while not (-180 <= self.measures.compass <= -165 or 165 <= self.measures.compass <= 180):
                                self.driveMotors(0.08,-0.02)
                                self.readSensors()
                                self.move_in_line()
                        elif self.beacon_maze[y][x-1]=='1':
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
                        if self.beacon_maze[y][x+1]=='1':
                            if self.beacon_maze[y-1][x]!='1':
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
                        elif (self.beacon_maze[y][x+1]=='0' and self.beacon_maze[y-1][x]=='0') or self.beacon_maze[y-1][x]=='x':
                            self.driveMotors(0.10,0.10)
                            self.readSensors()
                            if self.measures.lineSensor[3]=='1':
                                if self.beacon_maze[y][x+1] != '1':
                                    self.beacon_maze[y][x+1] = 'x'
                            else:
                                self.driveMotors(0.15,-0.15)
                        elif self.beacon_maze[y][x+1]=='x':
                            while not (-15 <= self.measures.compass <= 15):
                                self.driveMotors(0.08,-0.02)
                                self.readSensors()
                                self.move_in_line()
                        elif self.beacon_maze[y][x+1]=='1':
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
                if self.beacon_maze[y][x]=='x':
                    print(f"PONTO - ({y},{x}) - {self.beacon_maze[y][x]}")
                    count = 0
                    if (self.beacon_maze[y][x+1]=='1' and self.beacon_maze[y+1][x]=='1') or (self.beacon_maze[y][x+1]=='1' and self.beacon_maze[y-1][x]=='1') or (self.beacon_maze[y][x-1]=='1' and self.beacon_maze[y+1][x]=='1') or (self.beacon_maze[y][x-1]=='1' and self.beacon_maze[y-1][x]=='1'):
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

    def find_path(self,xInitial,yInitial,xEnd,yEnd):
        print("FINDING PATH")
        node_initial = Node(None,(yInitial,xInitial),0,0,0)
        end_node = Node(None,(yEnd,xEnd),0,0,0)

        open_list=[]
        closed_list = []

        open_list.append(node_initial)

        while len(open_list) > 0:
            print("On while")
            current_node = open_list[0]
            print(current_node,"inicio")
            print(end_node,"fim")
            current_index = 0
            for index,item in enumerate(open_list):
                if item.f < current_node.f:
                    current_node = item
                    current_index = index

            open_list.pop(current_index)
            closed_list.append(current_node)

            if current_node.position == end_node.position:
                print("getting path")
                path = []
                current = current_node
                while current is not None:
                    path.append(current.position)
                    current = current.parent
                return path[::-1]

            children = []
            for new_position in [(0,-1),(0,1),(-1,0),(1,0)]:
                node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])
                if node_position[0] > (len(self.beacon_maze) - 1) or node_position[0] < 0 or node_position[1] > (len(self.beacon_maze[len(self.beacon_maze)-1]) -1) or node_position[1] < 0:
                    continue
                if self.beacon_maze[node_position[0]][node_position[1]] == '0':
                    continue
                new_node = Node(current_node, node_position)
                children.append(new_node)

            for child in children:
                for closed_child in closed_list:
                    if child == closed_child:
                        continue
                child.g = current_node.g + 1
                child.h = ((child.position[0] - end_node.position[0])**2) + ((child.position[1] - end_node.position[1])**2)
                child.f = child.g + child.h
                for open_node in open_list:
                    if child == open_node and child.g > open_node.g:
                        continue
                open_list.append(child)

    def found_all_beacons(self,initialX,initialY):
        #self.beacon_maze is the maze with 0's and 1's
        #self.beacon_coords is the list of (y,x) coordinates of the beacons
        for i in range(len(self.beacon_coords)):
            self.beacon_coords[i][0] = self.beacon_coords[i][0]
            self.beacon_coords[i][1] = self.beacon_coords[i][1]

        print("INICIO",self.beacon_maze[initialY][initialX])
        #replace 'x' with '1' in the maze
        #iterate over the maze
        for linha in range(len(self.beacon_maze)):
            for coluna in range(len(self.beacon_maze[linha])):
                if self.beacon_maze[linha][coluna] == 'x':
                    self.beacon_maze[linha][coluna] = '1'


        # for i in range(len(self.beacon_maze)):
        #     for x in range(len(self.beacon_maze[i])):
        #         if self.beacon_maze[i][x] == 'x':
        #             self.beacon_maze[i][x] == '1'
        print(self.beacon_maze)
        print("INICIO2",self.beacon_maze[initialY][initialX])
        self.orderedBeacons = []
        print(self.beacon_coords,"BEACON COORDS")
        final_path=[]
        if len(self.beacon_coords)!=0:
            for i in self.beacon_coords:
                coordY,coordX = self.find_next_destiny(initialY,initialX)
                self.orderedBeacons.append((coordY,coordX))
            self.orderedBeacons.insert(len(self.orderedBeacons)-1,self.orderedBeacons.pop(0))

        if len(self.orderedBeacons)!=0:
            for i in range(len(self.orderedBeacons)-1):
                path = self.find_path(initialX,initialY,self.orderedBeacons[i][1],self.orderedBeacons[i][0])
                print(final_path,"FINAL PATH")
                print(path,"PATH")
                if final_path==[]:
                    final_path = path
                
                elif final_path[-1] == path[0]:
                    final_path = final_path + path[1:]
                else:
                    final_path = final_path + path
                initialX = coordX
                initialY = coordY
                
        print("PATH FINAL: ",final_path)

    def find_next_destiny(self,initialY,initialX):
        src = Pair(initialY, initialX)
        shortest_path = 0
        index = 0
        for i in range(len(self.beacon_coords)):
            if i==0:
                shortest_path = self.findShortestPathLength(self.beacon_maze, src, Pair(self.beacon_coords[i][1], self.beacon_coords[i][0]))
                if (shortest_path != -1):
                    print("Shortest Path is", shortest_path)
                
                else:
                    print("Shortest Path doesn't exist")
                    return None

                index = 0
            else:
                temp_path = self.findShortestPathLength(self.beacon_maze, src, Pair(self.beacon_coords[i][1], self.beacon_coords[i][0]))
                if (temp_path != -1):
                    print("Shortest Path is", dist)
                
                else:
                    print("Shortest Path doesn't exist")
                    return None

                if temp_path < shortest_path:
                    shortest_path = temp_path
                    index = i
        return self.beacon_coords.pop(index)

    def isSafe(self,mat, visited, y, x):
        print(y,x,'0')
        print(x>=0,"1")
        print(x<len(mat[0]),"2")
        print(y>=0,"3")
        print(y<len(mat),"4")
        print(mat[y][x] == '1',"5")
        print(mat[y][x],'5.5')
        print(not visited[y][x],"6")
        return (y >= 0 and y < len(mat) and x >= 0 and x < len(mat[0]) and mat[y][x] == '1' and (not visited[y][x]))

    def findShortestPath(self,mat, visited, j, i, y, x, min_dist, dist):
        print(j,i,"random")
        # input()

        if (i == x and j == y):
            min_dist = min(dist, min_dist)
            return min_dist

        # set (i, j) cell as visited
        visited[j][i] = True
        
        # go to the bottom cell
        if (self.isSafe(mat, visited, j+1, i)):
            print("baixo")
            min_dist = self.findShortestPath(
                mat, visited, j+1, i, y , x, min_dist, dist + 1)

        # go to the right cell
        if (self.isSafe(mat, visited, j, i+1)):
            print("direita")
            min_dist = self.findShortestPath(
                mat, visited, j, i+1, y, x, min_dist, dist + 1)

        # go to the top cell
        if (self.isSafe(mat, visited,j-1,i)):
            print("cima")
            min_dist = self.findShortestPath(
                mat, visited, j-1, i, y, x, min_dist, dist + 1)

        # go to the left cell
        if (self.isSafe(mat, visited, j,i-1)):
            print("esquerda")
            min_dist = self.findShortestPath(
                mat, visited, j,i-1, y, x, min_dist, dist + 1)

        # backtrack: remove (i, j) from the visited matrix
        visited[j][i] = False
        return min_dist

    # Wrapper over findShortestPath() function
    def findShortestPathLength(self,mat, src, dest):
        print(dest.first,dest.second,"destino")
        print(src.first,src.second,"fonte")
        if (len(mat) == 0 or mat[src.first][src.second] == 0
                or mat[dest.first][dest.second] == 0):
            return -1

        row = len(mat)
        col = len(mat[0])

        # construct an `M × N` matrix to keep track of visited
        # cells
        visited = []
        for i in range(row):
            visited.append([None for _ in range(col)])

        dist = sys.maxsize
        dist = self.findShortestPath(mat, visited, src.first,
                                src.second, dest.first, dest.second, dist, 0)

        if (dist != sys.maxsize):
            return dist
        return -1

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
        self.parent = parent
        self.position = position
        self.g = g
        self.h = h
        self.f = f

    def __str__(self) -> str:
        return str(self.position)

# User defined Pair class
class Pair:
    def __init__(self, x, y):
        self.first = int(x)
        self.second = int(y)


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
