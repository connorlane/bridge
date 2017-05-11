import math
from random import randint

# Create a random color as a string with the format: #rrggbb #
def randomColor():
    de=("%02x"%randint(0,255))
    re=("%02x"%randint(0,255))
    we=("%02x"%randint(0,255))
    ge="#"
    color=ge+de+re+we
    return color

# Utility function for calculating distance between two 2d points
def dist(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

