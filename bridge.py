from Tkinter import *
import numpy as np
import math
from enum import Enum
from random import randint, choice
import random
import copy

master = Tk()

w = Canvas(master, width=800, height=400)
w.pack()

P1 = (100, 100)
P2 = (300, 200)
P3 = (500, 200)
P4 = (700, 100)
P5 = (700, 300)
P6 = (100, 300)

class NodeType(Enum):
    NORMAL = 1
    ENTER_CS = 2
    EXIT_CS = 3

class State(Enum):
    NONE = 1
    AWAITING_CS = 2
    IN_CS = 3

path = (
        (P1, NodeType.NORMAL),
        (P2, NodeType.ENTER_CS), 
        (P3, NodeType.EXIT_CS),
        (P4, NodeType.NORMAL),
        (P5, NodeType.NORMAL),
        (P3, NodeType.ENTER_CS),
        (P2, NodeType.EXIT_CS),
        (P6, NodeType.NORMAL)
       )


def drawPath():
    for i in xrange(-1, len(path) - 1):
        w.create_line(path[i][0], path[i+1][0])

def dist(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def getPathLength(p):
    pathLength = 0
    for i in xrange(-1, len(path) - 1):
        pathLength = pathLength + dist(path[i][0], path[i+1][0])

    return pathLength

def getPosition(x):
    pathLength = getPathLength(path)
    distance = x * pathLength
    
    i = 0 
    done = False
    criticalSection = False
    while not done:
        i1 = i % len(path)
        i2 = (i+1) % len(path)
        p1 = path[i1][0]
        p2 = path[i2][0]

        if path[i1][1] == NodeType.ENTER_CS:
            criticalSection = True
        else:
            criticalSection = False

        segmentLength = dist(p1, p2)
        if distance > segmentLength:
            distance = distance - segmentLength
            i = i + 1
        else:
            position = (p1[0] + distance * (p2[0] - p1[0]) / segmentLength, 
                         p1[1] + distance * (p2[1] - p1[1]) / segmentLength)
            done = True

    return position, criticalSection, i

class Dude:
    RADIUS = 7
    dudeList = []
    idCounter = 0

    def __init__(self, color, speed, startPosition, swaggerRate):
        self.id = Dude.idCounter
        Dude.idCounter = Dude.idCounter + 1
        self.state = State.NONE
        self.inqueue = []
        self.swaggerRate = swaggerRate
        self.swaggerVelocity = (0, 0)
        self.swaggerCoords = (0, 0)
        self.outqueue = []
        self.color = color
        self.speed = speed
        self.position = startPosition
        self.coords, _, _ = getPosition(0)
        self.awaitingReply = dict()
        self.respondList = []
        for dude in Dude.dudeList:
            if dude != self:
                self.awaitingReply[dude] = False

    def receiveMessage(self):
        if len(self.inqueue) > 0:
            m = self.inqueue.pop()
            #print "Message Received: ", m[0].id, self.id, m[1]
            return m

    def sendMessage(otherDude, m):
        #print "Message Sent: ",  m[0].id, otherDude.id, m[1]
        otherDude.inqueue.insert(0, m)

    def timeStep(self, t):

        self.swaggerVelocity = (self.swaggerVelocity[0] - self.swaggerCoords[0]*self.swaggerRate*t - 0.02*self.swaggerVelocity[0]*t + 0.05*random.uniform(-1, 1)*t,
                                self.swaggerVelocity[1] - self.swaggerCoords[1]*self.swaggerRate*t - 0.02*self.swaggerVelocity[1]*t + 0.05*random.uniform(-1, 1)*t)

        self.swaggerCoords = (self.swaggerCoords[0] + self.swaggerVelocity[0],
                         self.swaggerCoords[1] + self.swaggerVelocity[1])


        if self.state == State.AWAITING_CS:
            m = self.receiveMessage()
            while m:
                if m[1] == 'v':
                    self.awaitingReply[m[0]] = 2
                elif m[1] == 'c' and m[2] == self.direction:
                    self.awaitingReply[m[0]] = 1
                elif m[1] == 'p':
                    if m[1] < self.id:
                        sendMessage(dude, (self, 'v'))
                    else:
                        self.respondList.insert(0, m[0])
                m = self.receiveMessage()

            dudesGoingMyDirection = 0
            stillWaiting = False
            for _, awaiting in self.awaitingReply.iteritems():
                if awaiting == 0:
                    stillWaiting = True
                    break
                elif awaiting == 1:
                    dudesGoingMyDirection = dudesGoingMyDirection + 1

            if not stillWaiting and dudesGoingMyDirection < 5:
                # Send messages to all my dudes letting them know I'm going
                #     into the crit section
                #print self.id, "enters the critical section"
                for mydude in self.respondList:
                    Dude.sendMessage(mydude, (self, 'c', self.direction))
                self.state = State.IN_CS

        elif self.state == State.NONE:
            m = self.receiveMessage()
            while m:
                if m[1] == 'p':
                    Dude.sendMessage(m[0], (self, 'v'))
                m = self.receiveMessage()

            self.position = (self.position + self.speed * t) % 1.0
            coords, criticalSection, i = getPosition(self.position)
            if criticalSection:
                #self.coords = self.coords[0] + randint(-15,15), self.coords[1] + randint(-15,15)
                self.state = State.AWAITING_CS
                self.direction = i
                for dude in Dude.dudeList:
                    if dude == self:
                        continue
                    Dude.sendMessage(dude, (self, 'p'))
                    self.awaitingReply[dude] = 0
            else:
                self.coords = coords

        elif self.state == State.IN_CS:
            m = self.receiveMessage()
            while m:
                if m[1] == 'p':
                    Dude.sendMessage(m[0], (self, 'c', self.direction))
                    self.respondList.insert(0, m[0])
                m = self.receiveMessage()

            self.position = (self.position + self.speed * t) % 1.0
            self.coords, criticalSection, _ = getPosition(self.position)
            if not criticalSection:
                while len(self.respondList) > 0:
                    Dude.sendMessage(self.respondList.pop(), (self, 'v'))
                self.state = State.NONE
                    
    def draw(self, w):
        x, y = self.coords
        swag_x, swag_y = self.swaggerCoords
        x = x + swag_x
        y = y + swag_y
        w.create_oval(x-self.RADIUS, y-self.RADIUS, x+self.RADIUS, y+self.RADIUS, fill=self.color)
        w.create_text(x, y, text=str(self.id))

def randomColor():
    de=("%02x"%randint(0,255))
    re=("%02x"%randint(0,255))
    we=("%02x"%randint(0,255))
    ge="#"
    color=ge+de+re+we
    return color

t = 1.5

for _ in xrange(0, 40): 
    startPosition = choice([random.uniform(0.3, 0.5)]) #random.uniform(0.8, 1.0)])
    Dude.dudeList.append(Dude(randomColor(), random.uniform(0.001, 0.0015), startPosition, 0.001))

while True:
    master.after(10)
    w.delete("all")

    drawPath()
    for dude in Dude.dudeList:
        dude.timeStep(t)
        dude.draw(w)

    w.update()

mainloop()

