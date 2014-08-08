musci
=====

Control [MOSS](http://www.modrobotics.com/moss/) [Double
Brain](http://www.modrobotics.com/moss/modules/double-brain/) using Python

**DISCLAIMER: The author and the repository contents are _not_ associated in
any way with [Modular Robotics](http://www.modrobotics.com/). The code
presented here is _not_ based on any official documentation and using it may
or may not damage your device. Use it at your own risk.**


Introduction
============

[MOSS](http://www.modrobotics.com/moss/) is a great robotics kit by [Modular
Robotics](http://www.modrobotics.com/), it features a bluetooth communications
module called [Double
Brain](http://www.modrobotics.com/moss/modules/double-brain/). The module can
be controlled using [mobile
apps](https://www.modrobotics.com/moss/moss-brain-instructions/), and also by
using the [Scratch programming
language](http://www.modrobotics.com/moss/apps/moss-scratch/). This
repository provides an API in Python for controlling the brain module.


Setup
=====

Setting up bluetooth can be tricky, at a minimum, the brain device needs to be
paired with a bluetooth enabled computer. The operating system needs to
support Python and the Python BlueZ bindings. The code was developed and
tested on an Asus 1000he EeePC running Ubuntu 14.04.

It is probably best to start by following the information in the links in the
Introduction section above and setup the mobile apps and/or the Scratch
environment, then connect to the device and communicate with it. Doing so,
will help in gaining familiarity with the setup, the device and its
capabilities and provide an opportunity to troubleshoot possible issues in a
more "friendly" environment.


The musci Python Module
=======================

The `musci.py` script contains inline documentation for the API that it
exposes (try running `import musci; help(musci)` and also read the code).
The API allows connecting to (and scanning for, if needed) the brain
bluetooth device, and then sending commands to the device to set and get
parameters, such as face input/output state, value and LED color.

The `Brain` class is used in a `with` statement to instantiate an object.
This will optionally scan for, and connect to the device. This instance
object is then used as a function (callable) to issue commands to the
device, the return value of the function call is that output data from the
command.

    ```python
    import musci
    with musci.Brain() as brain:
        brain('setLEDState', 255, 0, 0)
        r, g, b = brain('getLEDState')
        ...
    ```

For now, _only_ the following commands were tested:

- `getAllFaceStates`:
  - Input: empty
  - Output: STATE-1, VALUE-1, STATE-2, VALUE-2, ..., STATE-8, VALUE-8

- `setAllFaceStates`:
  - Input: STATE-1, STATE-2, ..., STATE-8
  - Output: VALUE-1, VALUE-2, ..., VALUE-8

- `setFaceState`:
  - Input: ZERO-BASED-INDEX, STATE
  - Output: ZERO-BASED-INDEX, VALUE

- `getAllFaceValues`:
  - Input: empty
  - Output: VALUE-1, VALUE-2, ..., VALUE-8

- `getFaceValue`:
  - Input: ZERO-BASED-INDEX
  - Output: ZERO-BASED-INDEX, VALUE

- `setManyFaceValues`:
  - Input: INDEX-MASK, FIRST-VALUE, SECOND-VALUE, ..., LAST-VALUE
  - Output: empty

- `setFaceValue`:
  - Input: ZERO-BASED-INDEX, VALUE
  - Output: empty

- `getLEDState`:
  - Input: empty
  - Output: RED-VALUE, GREEN-VALUE, BLUE-VALUE

- `setLEDState`:
  - Input: RED-VALUE, GREEN-VALUE, BLUE-VALUE
  - Output: empty

Scanning and connecting can take some time (>10 seconds), it can be
shortened if the device address is provided when the `Brain` object is
initialized, but it still takes a few seconds to connect.

The API is implemented with synchronous I/O, a command call will block until
the result of the command is available. When the bluetooth connection is weak
the command call would just appear to be stuck - this can be confusing.

When `musci.py` is run as a script it will function as a "server" that
listens for commands on `stdin`, runs them on the device and writes the
output to `stdout`. This can be used to interface with the device from the
shell. If `-d` is used (as in `./musci.py -d`), a lot of debugging messages
will be printed, with (among other things) the address of the device that can
be used to connect more quickly if it is specified with `-a ADDRESS`.


Examples
========

There are two example scripts: `led.py` and `rover.py`. Like `musci.py`,
they can be launched with `-a ADDRESS` to speed up the connection setup
time, and with `-d` to generate (lots of) debug messages. The scripts run
forever and are supposed to be stopped by CTRL-C. The scripts are each
intended to control a specific robot with a bluetooth brain that has
specific faces connected to the proximity sensor and (for `rover.py`) the
wheels.

- `led.py`: control a simple distance measuring device made from the
  battery block, the double brain block, and the proximity sensor
  (connected to face #7 in the brain block). The script will periodically
  read the output of the proximity sensor and will set the LED color
  according to the measured proximity value.

- `rover.py`: control an obstacle evading "rover" built with two parallel
  wheels (connected to faces #1 and #8) and the proximity sensor (connected
  to face #7). The script will instruct the rover to move the wheels forward
  for a period of time, then read the proximity sensor value, then if there
  is an object in front of the proximity sensor, the script will move the
  wheels backward for a period of time, then turn for a period of time, then
  try again to move forward.


Why musci?
==========

MOSS is a trademark of Modular Robotics, and Musci is the Latin word for
Mosses (the plants).
