from enum import Enum
import path
import random

RADIUS = 8

PARAMETERS = {
        "radius": 8,
        "masterDudeList": [],
        "maxDudesInCS": 2,
        "swagRateConstant": 0.001,
        "swagDampingConstant": 0.02,
        "swagExcitationConstant": 0.05
        }
            
# Class for the moving blobs, a.k.a. dudes
class Dude:
    idCounter = 0

    def __init__(self, color, speed, startPosition):
        self.id = Dude.idCounter
        Dude.idCounter = Dude.idCounter + 1
        self.state = Dude.State.NONE
        self.inqueue = []
        self.swaggerVelocity = (0, 0)
        self.swaggerCoords = (0, 0)
        self.outqueue = []
        self.color = color
        self.speed = speed
        self.position = startPosition
        self.coords, _, _ = path.getCoordinates(0)
        self.awaitingReply = dict()
        self.respondList = []
        for dude in PARAMETERS['masterDudeList']:
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

    # Updates the dude swag (oscillation effect) for a given amount of time elapsed
    def _updateSwagger(self, t):
        self.swaggerVelocity = (
                                self.swaggerVelocity[0]
                                - PARAMETERS['swagRateConstant']*self.swaggerCoords[0]*t
                                - PARAMETERS['swagDampingConstant']*self.swaggerVelocity[0]*t
                                + PARAMETERS['swagExcitationConstant']*random.uniform(-1, 1)*t,

                                self.swaggerVelocity[1]
                                - PARAMETERS['swagRateConstant']*self.swaggerCoords[1]*t
                                - PARAMETERS['swagDampingConstant']*self.swaggerVelocity[1]*t
                                + PARAMETERS['swagExcitationConstant']*random.uniform(-1, 1)*t
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
                    # Record that the dude has given us the all clear
                    self.awaitingReply[m[0]] = Dude.ReplyState.ALL_CLEAR
                elif m[1] == Dude.MessageCode.NOTIFY_CS_DIRECTION and m[2] == self.direction:
                    # This dude is in the CS, but he's going the same direction as us
                    self.awaitingReply[m[0]] = Dude.ReplyState.SAME_DIRECTION
                elif m[1] == Dude.MessageCode.REQUEST_CS:
                    # This dude wants to enter the CS, but we can't let him do that, Dave
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
                    # Count up the dudes going the same direction as me
                    dudesGoingMyDirection = dudesGoingMyDirection + 1

            if not stillWaiting and dudesGoingMyDirection < PARAMETERS['maxDudesInCS']:
                # Send messages to all my dudes letting them know I'm going
                #     into the critical section
                for mydude in self.respondList:
                    #print 'Yo, Dude #', mydude.id, '. Dude #', self.id, 'is in the crit section going direction #', self.direction
                    self.sendMessage(mydude, (Dude.MessageCode.NOTIFY_CS_DIRECTION, self.direction))

                # Go into the critical section
                print 'Dude #', self.id, 'entering the critical section'
                self.state = Dude.State.IN_CS

        # STATE: Moving in loop, not awaiting critical section #
        elif self.state == Dude.State.NONE:

            # Check messages
            m = self.receiveMessage()
            while m:
                if m[1] == Dude.MessageCode.REQUEST_CS:
                    # We're not trying to get into the CS, so give the go-ahead
                    self.sendMessage(m[0], (Dude.MessageCode.NOTIFY_CS_ALLCLEAR,))
                    #print 'Sup, Dude #', m[0].id, '. Dude #', self.id, 'gives you the all clear.'
                m = self.receiveMessage()

            # Calculate the current position. Position is normalized so that 1.0 is one full loop
            self.position = (self.position + self.speed * t) % 1.0
            coords, criticalSection, direction = path.getCoordinates(self.position)

            # If we're entering a critical section...
            if criticalSection:

                # Switch states
                self.state = Dude.State.AWAITING_CS

                # Record which direction we're trying to go
                self.direction = direction

                # For each other dude, send a message to let them know we want in the CS
                for dude in PARAMETERS['masterDudeList']:
                    if dude == self:
                        continue
                    self.sendMessage(dude, (Dude.MessageCode.REQUEST_CS,))
                    #print 'Hey, Dude #', dude.id, 'can Dude #', self.id, 'enter the critical section?'
                    # Load of the ReplyState data structure with the default
                    #   value of 'no response'
                    self.awaitingReply[dude] = Dude.ReplyState.NO_RESPONSE
            else:
                # Not in critical section, so update the coordinates to move forward
                self.coords = coords

        # STATE: Currently moving through the CS #
        elif self.state == Dude.State.IN_CS:

            # Check messages
            m = self.receiveMessage()
            while m:
                if m[1] == Dude.MessageCode.REQUEST_CS:
                    # Let the requesting dude know what direction I'm going
                    self.sendMessage(m[0], (Dude.MessageCode.NOTIFY_CS_DIRECTION, self.direction))
                    #print 'Yo, Dude #', m[0].id, '. Dude #', self.id, 'is in the crit section going direction #', self.direction

                    # Record this dude so I can notify him when I leave the CS
                    self.respondList.insert(0, m[0])

                m = self.receiveMessage()

            # Update the position, moving forward through the critical section
            self.position = (self.position + self.speed * t) % 1.0
            self.coords, criticalSection, _ = path.getCoordinates(self.position)

            # Check if we've exited the critical section
            if not criticalSection:
                # Let all the dudes who've requested access to the CS know that I'm leaving
                #   the CS now
                while len(self.respondList) > 0:
                    mydude = self.respondList.pop()
                    self.sendMessage(mydude, (Dude.MessageCode.NOTIFY_CS_ALLCLEAR,))
                    #print 'Sup, Dude #', mydude.id, '. Dude #', self.id, 'gives you the all clear.'

                # Return to non-cs state
                print 'Dude #', self.id, 'exiting the critical section'
                self.state = Dude.State.NONE
                
    # Draw as a circle on the specified canvas object #
    def draw(self, w):
        # Build the current coordinates #
        x = self.coords[0] + self.swaggerCoords[0]
        y = self.coords[1] + self.swaggerCoords[1]

        # Draw the circle and ID label
        w.create_oval(x-PARAMETERS['radius'], 
                      y-PARAMETERS['radius'], 
                      x+PARAMETERS['radius'], 
                      y+PARAMETERS['radius'], 
                      fill=self.color)

        # Draw ID label within the circle
        w.create_text(x, y, text=str(self.id))


