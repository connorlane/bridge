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

# Default control parameters

DEFAULT_MAXDUDESINCS = 3
DEFAULT_NUMDUDES = 20
DEFAULT_SPEED = 1.0



# Create a window object
master = Tk()

# Create window frame for control elements
f_controls = Frame()
f_controls.pack(pady=20)

# Create window frame for canvas element
f_canvas = Frame()
f_canvas.pack()

# Populate control frame with user controls
f_speed = Frame(f_controls)
f_speed.pack(side=LEFT, padx=20)
l_speed = Label(f_speed, text="Speed of Motion:", )
l_speed.pack()
s_speed = Scale(f_speed, from_=0, to=15, orient=HORIZONTAL, resolution=0.05)
s_speed.set(DEFAULT_SPEED)
s_speed.pack()

f_maxNumDudes = Frame(f_controls)
f_maxNumDudes.pack(side=LEFT, padx=20)
l_maxNumDudes = Label(f_maxNumDudes, text="Maximum Dudes on the Bridge:")
l_maxNumDudes.pack()
v_maxNumDudes = StringVar()
e_maxNumDudes = Entry(f_maxNumDudes, textvariable=v_maxNumDudes)
v_maxNumDudes.set(str(DEFAULT_MAXDUDESINCS))
e_maxNumDudes.pack()

f_numDudes = Frame(f_controls)
f_numDudes.pack(side=LEFT, padx=20)
l_numDudes = Label(f_numDudes, text="Number of Dudes In the System:")
l_numDudes.pack()
s_numDudes = Scale(f_numDudes, from_=0, to=100, orient=HORIZONTAL)
s_numDudes.set(DEFAULT_NUMDUDES)
s_numDudes.pack()

# Create a canvas object within the window
w = Canvas(f_canvas, width=800, height=400)
w.pack()

# Create N nodes
for _ in xrange(0, 10): 
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
    # Collect user paramters
    try:
        t = s_speed.get()
    except:
        pass

    try:
        dude.PARAMETERS['maxDudesInCS'] = int(v_maxNumDudes.get())
    except:
        dude.PARAMETERS['maxDudesInCS'] = 0

    try:
        targetNumDudes = s_numDudes.get()
        numberOfDudesToCreate = targetNumDudes - len(dude.PARAMETERS['masterDudeList'])
        if numberOfDudesToCreate > 0:
            for _ in xrange(numberOfDudesToCreate):
                startPosition = random.uniform(0.8, 0.99)
                dude.PARAMETERS['masterDudeList'].append(
                    dude.Dude(
                        util.randomColor(),             # Dude Color
                        random.uniform(0.001, 0.0012),  # Average speed of travel
                        startPosition,                  # Initial dude position
                        )
                    )
        elif numberOfDudesToCreate < 0:
            numberOfDudesToDestroy = -numberOfDudesToCreate
            for _ in xrange(numberOfDudesToDestroy):
                # Actually delete this so it will clean itself up and notify other dudes of it's
                #   demise appropriately.
                #
                #   ... Otherwise ghostly dude...
                dude.PARAMETERS['masterDudeList'].pop().cleanup()

    except:
        pass

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

