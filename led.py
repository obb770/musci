#!/usr/bin/env python

# The contents of this file are placed in the public domain.

import sys
import time

import musci

# Change 7 below to the actual face number to which the proximity sensor is
# connected.
SENSOR = 7 - 1

POLLING_PERIOD = .1

with musci.Brain(sys.argv) as brain:
    brain('setFaceState', SENSOR, musci.INPUT)
    while True:
        command, val = brain('getFaceValue', SENSOR)
        index = int(val / 32.)
        brain('setLEDState', *musci.COLORS[index])
        time.sleep(POLLING_PERIOD)
