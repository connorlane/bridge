from Tkinter import *
import numpy as np
import math
from enum import Enum
from random import randint
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

    return position, criticalSection

class Dude:
    RADIUS = 7
    dudeList = []
    idCounter = 0

    def __init__(self, color, speed):
        self.id = Dude.idCounter
        Dude.idCounter = Dude.idCounter + 1
        self.state = State.NONE
        self.inqueue = []
        self.outqueue = []
        self.color = color
        self.speed = speed
        self.position = 0
        self.coords, _ = getPosition(0)
        self.awaitingReply = dict()
        for dude in Dude.dudeList:
            if dude != self:
                self.awaitingReply[dude] = False

    def receiveMessage(self):
        if len(self.inqueue) > 0:
            m = self.inqueue.pop()
            print "Message Received: ", m[0].id, self.id, m[1]
            return m

    def sendMessage(otherDude, m):
        print "Message Sent: ",  m[0].id, otherDude.id, m[1]
        otherDude.inqueue.insert(0, m)

    def timeStep(self, t):
        if self.state == State.AWAITING_CS:
            m = self.receiveMessage()
            while m:
                if m[1] == 'v':
                    self.awaitingReply[m[0]] = False
                elif m[1] == 'p':
                    if m[1] < self.id:
                        sendMessage(dude, (self, 'v'))
                    else:
                        self.respondList.insert(0, m[0])
                m = self.receiveMessage()

            stillWaiting = False
            for _, awaiting in self.awaitingReply.iteritems():
                if awaiting == True:
                    stillWaiting = True
                    break
            if not stillWaiting:
                self.state = State.IN_CS

        elif self.state == State.NONE:
            m = self.receiveMessage()
            while m:
                if m[1] == 'p':
                    Dude.sendMessage(m[0], (self, 'v'))
                m = self.receiveMessage()

            self.position = (self.position + self.speed * t) % 1.0
            coords, criticalSection = getPosition(self.position)
            if criticalSection:
                self.state = State.AWAITING_CS
                for dude in Dude.dudeList:
                    if dude == self:
                        continue
                    Dude.sendMessage(dude, (self, 'p'))
                    self.awaitingReply[dude] = True
            else:
                self.coords = coords
        elif self.state == State.IN_CS:
            m = self.receiveMessage()
            while m:
                if m[1] == 'p':
                    self.respondList.insert(0, m[0])

            self.position = (self.position + self.speed * t) % 1.0
            coords, criticalSection = getPosition(self.position)
            if not criticalSection:
                while len(self.respondList) > 0:
                    sendMessage(self.respondList.pop(), (self, 'v'))
                self.state = State.NONE
                    
    def draw(self, w):
        x, y = self.coords
        w.create_oval(x-self.RADIUS, y-self.RADIUS, x+self.RADIUS, y+self.RADIUS, fill=self.color)

t = 1
Dude.dudeList.append(Dude("red", 0.001))
Dude.dudeList.append(Dude("green", 0.002))
Dude.dudeList.append(Dude("blue", 0.003))
while True:
    master.after(10)
    w.delete("all")

    drawPath()
    for dude in Dude.dudeList:
        dude.timeStep(t)
        dude.draw(w)

    w.update()


mainloop()

