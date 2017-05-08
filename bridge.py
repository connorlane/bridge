from Tkinter import *
import numpy as np
import math
from enum import Enum
from random import randint, choice
import random
import copy

# Draw the path on the specified canvas object
def drawPath():
    for i in xrange(-1, len(path) - 1):
        w.create_line(path[i][0], path[i+1][0])

# Utility function for calculating distance between two 2d points
def dist(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# Calculates the total length of the given path
def getPathLength(p):
    pathLength = 0
    for i in xrange(-1, len(path) - 1):
        pathLength = pathLength + dist(path[i][0], path[i+1][0])

    return pathLength

# Gets coordinates from path position. x represents distance along the loop path.
#   x is normalized so that 1.0 is one full loop path. 0.5 is half way through the
#   loop, etc. This function takes a value from 0.0 to 1.0 and converts to x, y
#   coordinates along the path. Also returns whether or not the position is within
#   a critical section
def getCoordinates(x):
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
    maxDudesOnBridge = 7

    def __init__(self, color, speed, startPosition, swaggerRate):
        self.id = Dude.idCounter
        Dude.idCounter = Dude.idCounter + 1
        self.state = Dude.State.NONE
        self.inqueue = []
        self.swaggerRate = swaggerRate
        self.swaggerVelocity = (0, 0)
        self.swaggerCoords = (0, 0)
        self.outqueue = []
        self.color = color
        self.speed = speed
        self.position = startPosition
        self.coords, _, _ = getCoordinates(0)
        self.awaitingReply = dict()
        self.respondList = []
        for dude in Dude.dudeList:
            if dude != self:
                self.awaitingReply[dude] = False

    # Receive a message from another dude
    def receiveMessage(self):
        if len(self.inqueue) > 0:
            m = self.inqueue.pop()
            return m

    # Send a message to another dude
    def sendMessage(self, otherDude, m):
        otherDude.inqueue.insert(0, (self,) + m)

    # Constants for the random oscillation effect
    #   Adjust to change amplitude, frequency and damping for the dudes movement
    SWAGGER_RATE_CONSTANT = 0.001
    SWAGGER_DAMPING_CONSTANT = 0.02
    SWAGGER_EXCITATION_CONSTANT = 0.05

    # Updates the dude swag (oscillation effect) for a given amount of time elapsed
    def _updateSwagger(self, t):
        self.swaggerVelocity = (
                                self.swaggerVelocity[0]
                                - Dude.SWAGGER_RATE_CONSTANT*self.swaggerCoords[0]*t
                                - Dude.SWAGGER_DAMPING_CONSTANT*self.swaggerVelocity[0]*t
                                + Dude.SWAGGER_EXCITATION_CONSTANT*random.uniform(-1, 1)*t,

                                self.swaggerVelocity[1]
                                - Dude.SWAGGER_RATE_CONSTANT*self.swaggerCoords[1]*t
                                - Dude.SWAGGER_DAMPING_CONSTANT*self.swaggerVelocity[1]*t
                                + Dude.SWAGGER_EXCITATION_CONSTANT*random.uniform(-1, 1)*t
                                )

        self.swaggerCoords = (
                              self.swaggerCoords[0]
                              + self.swaggerVelocity[0],

                              self.swaggerCoords[1]
                              + self.swaggerVelocity[1]
                              )

    # Enum for specifying status of replies from other dudes for entry to CS
    class ReplyState(Enum):
        NO_RESPONSE = 1
        SAME_DIRECTION = 2
        ALL_CLEAR = 3

    # Message codes for exchanging information between dudes
    class MessageCode(Enum):
        REQUEST_CS = 1
        NOTIFY_CS_DIRECTION = 2
        NOTIFY_CS_ALLCLEAR = 3

    # Enum for state machine states
    class State(Enum):
        NONE = 1
        AWAITING_CS = 2
        IN_CS = 3

    # Main time step fuction. Moves the dude <t> units of time forward
    #   Contains the main state machine for the dudes
    def timeStep(self, t):

        # Update the swagger values (random oscillations)
        self._updateSwagger(t)

        ## BEGIN STATE MACHINE ##

        # STATE: Waiting for entry to CS #
        if self.state == Dude.State.AWAITING_CS:
            # Check messages
            m = self.receiveMessage()
            while m:
                if m[1] == Dude.MessageCode.NOTIFY_CS_ALLCLEAR:
                    self.awaitingReply[m[0]] = Dude.ReplyState.ALL_CLEAR
                elif m[1] == Dude.MessageCode.NOTIFY_CS_DIRECTION and m[2] == self.direction:
                    self.awaitingReply[m[0]] = Dude.ReplyState.SAME_DIRECTION
                elif m[1] == Dude.MessageCode.REQUEST_CS:
                    self.respondList.insert(0, m[0])
                m = self.receiveMessage()

            # See if all dudes have replied. If there are less than N dudes going
            #   in my direction, go ahead and enter the critical section
            dudesGoingMyDirection = 0
            stillWaiting = False
            for _, awaiting in self.awaitingReply.iteritems():
                if awaiting == Dude.ReplyState.NO_RESPONSE:
                    stillWaiting = True
                    break
                elif awaiting == Dude.ReplyState.SAME_DIRECTION:
                    dudesGoingMyDirection = dudesGoingMyDirection + 1

            if not stillWaiting and dudesGoingMyDirection < Dude.maxDudesOnBridge:
                # Send messages to all my dudes letting them know I'm going
                #     into the critical section
                for mydude in self.respondList:
                    self.sendMessage(mydude, (Dude.MessageCode.NOTIFY_CS_DIRECTION, self.direction))
                self.state = Dude.State.IN_CS

        # STATE: Moving in loop, not awaiting critical section #
        elif self.state == Dude.State.NONE:

            # Check messages
            m = self.receiveMessage()
            while m:
                if m[1] == Dude.MessageCode.REQUEST_CS:
                    self.sendMessage(m[0], (Dude.MessageCode.NOTIFY_CS_ALLCLEAR,))
                m = self.receiveMessage()

            # Calculate the current position. Position is normalized so that 1.0 is one full loop
            self.position = (self.position + self.speed * t) % 1.0
            coords, criticalSection, i = getCoordinates(self.position)
            if criticalSection:
                self.state = Dude.State.AWAITING_CS
                self.direction = i
                for dude in Dude.dudeList:
                    if dude == self:
                        continue
                    self.sendMessage(dude, (Dude.MessageCode.REQUEST_CS,))
                    self.awaitingReply[dude] = Dude.ReplyState.NO_RESPONSE
            else:
                self.coords = coords

        # STATE: Currently moving through the CS #
        elif self.state == Dude.State.IN_CS:
            m = self.receiveMessage()
            while m:
                if m[1] == Dude.MessageCode.REQUEST_CS:
                    self.sendMessage(m[0], (Dude.MessageCode.NOTIFY_CS_DIRECTION, self.direction))
                    self.respondList.insert(0, m[0])
                m = self.receiveMessage()

            self.position = (self.position + self.speed * t) % 1.0
            self.coords, criticalSection, _ = getCoordinates(self.position)
            if not criticalSection:
                while len(self.respondList) > 0:
                    self.sendMessage(self.respondList.pop(), (Dude.MessageCode.NOTIFY_CS_ALLCLEAR,))
                self.state = Dude.State.NONE
                
    # Draw as a circle on the specified canvas object #
    def draw(self, w):
        # Build the current coordinates #
        x = self.coords[0] + self.swaggerCoords[0]
        y = self.coords[1] + self.swaggerCoords[1]

        # Draw the circle and ID label
        w.create_oval(x-self.RADIUS, y-self.RADIUS, x+self.RADIUS, y+self.RADIUS, fill=self.color)
        w.create_text(x, y, text=str(self.id))

# Create a random color as a string with the format: #rrggbb #
def randomColor():
    de=("%02x"%randint(0,255))
    re=("%02x"%randint(0,255))
    we=("%02x"%randint(0,255))
    ge="#"
    color=ge+de+re+we
    return color

# Create a window object
master = Tk()

# Create a canvas object within the window
w = Canvas(master, width=800, height=400)
w.pack()

# Path critical point definitions
P1 = (100, 100)
P2 = (300, 200)
P3 = (500, 200)
P4 = (700, 100)
P5 = (700, 300)
P6 = (100, 300)

# Enum to specify type of node within the path
class NodeType(Enum):
    NORMAL = 1
    ENTER_CS = 2
    EXIT_CS = 3

# Path definition. Defines how the points link together to define a loop path.
#   Also defines the critical section
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

# Calculate the path length
pathLength = getPathLength(path)

# Define a default timestep value
t = 10

# Create N nodes
for _ in xrange(0, 25): 
    startPosition = random.uniform(0.3, 0.5)
    Dude.dudeList.append(Dude(randomColor(), random.uniform(0.001, 0.0015), startPosition, 0.001))

# Main drawing loop
while True:
    # Refresh rate, 50Hz
    master.after(20)

    # Clear the canvas
    w.delete("all")

    # Draw the loop path on the canvas
    drawPath()

    # Update each dude, and draw them on the canvas
    for dude in Dude.dudeList:
        dude.timeStep(t)
        dude.draw(w)

    # Refresh the canvas
    w.update()

mainloop()

