from enum import Enum
import math
import util

## GLOBAL PATH DEFINITION & SETUP ##

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
pathLength = 0
for i in xrange(-1, len(path) - 1):
    pathLength = pathLength + util.dist(path[i][0], path[i+1][0])






## MAIN FUNCTION / CLASS DEFINITIONS ##

# Draw the path on the specified canvas object
def drawPath(canvas):
    for i in xrange(-1, len(path) - 1):
        canvas.create_line(path[i][0], path[i+1][0])

# Gets coordinates from path position. x represents distance along the loop path.
#   x is normalized so that 1.0 is one full loop path. 0.5 is half way through the
#   loop, etc. This function takes a value from 0.0 to 1.0 and converts to x, y
#   coordinates along the path. Also returns whether or not the position is within
#   a critical section
def getCoordinates(x):
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

        segmentLength = util.dist(p1, p2)
        if distance > segmentLength:
            distance = distance - segmentLength
            i = i + 1
        else:
            position = (p1[0] + distance * (p2[0] - p1[0]) / segmentLength, 
                         p1[1] + distance * (p2[1] - p1[1]) / segmentLength)
            done = True

    return position, criticalSection, i


