#!/usr/bin/env python

# The contents of this file are placed in the public domain.

import sys
import time

import musci

# Change 7 below to the actual face number to which the proximity sensor is
# connected.
SENSOR = 7 - 1

# Change (the first) 1 below to the actual face number to which the right
# wheel is connected.
RIGHT = 1 - 1

# Change 8 below to the actual face number to which the left wheel is
# connected.
LEFT = 8 - 1

FORWARD_SPEED = 200
BACKWARD_SPEED = 55

FORWARD_DURATION = .5
BACKWARD_DURATION = .4
TURN_DURATION = .6

with musci.Brain(sys.argv) as brain:
    def control(duration, left, right, red, green, blue):
        brain('setLEDState', red, green, blue)
        brain('setFaceValue', RIGHT, right)
        brain('setFaceValue', LEFT, left)
        time.sleep(duration)

    def forward(duration):
        control(duration, FORWARD_SPEED, FORWARD_SPEED, *musci.GREEN)

    def backward(duration):
        control(duration, BACKWARD_SPEED, BACKWARD_SPEED, *musci.RED)

    def turn(duration):
        control(duration, BACKWARD_SPEED, FORWARD_SPEED, *musci.YELLOW)

    brain('setFaceState', SENSOR, musci.INPUT)
    forward(0)
    while True:
        time.sleep(FORWARD_DURATION)
        command, val = brain('getFaceValue', SENSOR)
        if val < 85:
            continue
        backward(BACKWARD_DURATION)
        turn(TURN_DURATION)
        forward(0)
