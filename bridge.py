from Tkinter import *
import numpy as np
import math
from enum import Enum
from random import randint, choice
import random
import copy
import dude
import path
import util

# Create a window object
master = Tk()

# Create a canvas object within the window
w = Canvas(master, width=800, height=400)
w.pack()

# Define a default timestep value
t = 2.90

# Create N nodes
for _ in xrange(0, 27): 
    # Generate a random starting point on one side of the bridge
    startPosition = random.uniform(0.8, 0.99)
    dude.PARAMETERS['masterDudeList'].append(
        dude.Dude(
            util.randomColor(),             # Dude Color
            random.uniform(0.001, 0.0012),  # Average speed of travel
            startPosition,                  # Initial dude position
            )
        )

# Main drawing loop
while True:
    # Refresh rate, 50Hz
    master.after(20)

    # Clear the canvas
    w.delete("all")

    # Draw the loop path on the canvas
    path.drawPath(w)

    # Update each dude, and draw them on the canvas
    for mydude in dude.PARAMETERS['masterDudeList']:
        mydude.timeStep(t)
        mydude.draw(w)

    # Refresh the canvas
    w.update()

mainloop()

