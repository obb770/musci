#!/usr/bin/env python

# Copyright 2014 Ofer Barkai
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Low level API to control a double brain block over bluetooth.

Provide an API to connect and send commands to a double brain block
bluetooth device. It is possible to control the state of the block faces
(for input or output), to set and get the value of a face, to set the RGB
value of the LED. In the mobile apps and PC programming environment, face
numbers are in the range of 1-8 and the values are in the range of 0-100.
With this API, the face numbers are in the range of 0-7 and values in the
range of 0-255.
"""

import argparse
import logging
import sys

import bluetooth


__all__ = [
    'Brain',
    'NFACES', 'INPUT', 'OUTPUT',
    'BLACK', 'BLUE', 'GREEN', 'CYAN', 'RED', 'MAGENTA', 'YELLOW', 'WHITE',
    'COLORS']


NFACES = 8

INPUT = 1
OUTPUT = 0

code2command = {
    0x00: 'debug',
    0x01: 'getConfiguration',
    0x02: 'getMode',
    0x03: 'setMode',
    0x04: 'getAllFaceStates',
    0x05: 'setAllFaceStates',
    0x06: 'setFaceState',
    0x07: 'getAllFaceValues',
    0x08: 'getFaceValue',
    0x09: 'setManyFaceValues',
    0x0A: 'setFaceValue',
    0x0B: 'registerFaceValueEvent',
    0x0C: 'faceValueEvent',
    0x0D: 'getLEDState',
    0x0E: 'setLEDState',
    0x11: 'setAutoReconnect',
    0x12: 'setFaceOverride',
    0xF0: 'flash',
    0xF1: 'flashProgressEvent',
    0xF2: 'brickDetection'
}

command2code = {code2command[k]: k for k in code2command}

BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
RED = (255, 0, 0)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

COLORS = (BLACK, BLUE, GREEN, CYAN, RED, MAGENTA, YELLOW, WHITE)

logging.basicConfig(format='%(asctime)s.%(msecs)03d %(message)s',
    datefmt='%H:%M:%S')

class Brain(object):
    """Object for controlling a double brain block over bluetooth.

    Optionally scan for, connect and send commands to a brain bluetooth
    device.

    The object is initialized (optionally) with the bluetooth device
    address. The process is fastest if the address is specified. If no
    address is specified, then scan for a bluetooth device with a name
    beginning with specific prefix.

    This object is intended to be used with a "with" statement. When
    entering the "with" block, the bluetooth connection is created
    (preceded by a scan for the device if its address is not configured),
    and then the device settings are reset.  When exiting the "with"
    block, the settings are reset and the connection is closed.

    Commands are sent to the device by using the object as a function
    with the command and its data specified as argmuments to the function
    call.
    """

    def __init__(self, argv=None, address='', debug=False):
        """Configure the Brain object.

        Configure the address and whether to enable debug logging,
        Coniguration is done either through dedicated keyword arguments,
        or through options in argv.

        argv - use "-a ADDRESS" and "-d"
        address - brain device bluetooth address
        debug - enable debug logging
        """
        self.address = address
        self._debug = debug
        if argv:
            parser = argparse.ArgumentParser()
            parser.add_argument('-d', '--debug', dest='_debug',
                action='store_true', help='enable debug messages')
            parser.add_argument('-a', '--address',
                help='specify the bluetooth address')
            parser.parse_known_args(argv, self)

        logger = logging.getLogger(__name__ + '.' + self.address)
        if self._debug:
            logger.setLevel(logging.DEBUG)
        self.debug = logger.debug
        self.debug('starting...')

    def __call__(self, command, *args):
        """Send a command to the connected double brain block over bluetooth.

        Send the specified command with the given arguments and read back
        the response (except for commands that do not have a response).
        Return the response data.

        command - the string representation of the command to send
        args - arguments for command (integers in the range 0-255)

        Return: the result of the command as a list of integers
        """
        self.debug('%s: %s', command, args)
        seq = [ord('<'), command2code[command], 0, len(args), ord('>')]
        seq.extend(args)
        self.sock.send(''.join(['%c' % b for b in seq]))
        data = []
        if command not in set(['setManyFaceValues', 'setFaceValue']):
            header = self._read(5)
            body = self._read(ord(header[3]))
            data = [ord(c) for c in body]
            command = code2command[ord(header[1])]
        self.debug('%s: %s', command, data)
        return data

    def __enter__(self):
        """Connect to the double brain block over bluetooth."""
        try:
            self.sock = None
            self.connected = False
            if not self.address:
                self.debug('scanning...')
                self._scan()
            self.debug('connecting...')
            self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.sock.connect((self.address, 1))
            self.connected = True
            self._reset()
            return self
        except:
            self.__exit__(*sys.exc_info())
            raise

    def __exit__(self, type, value, traceback):
        """Reset the settings and close the bluetooth socket."""
        self.debug("stopping...")
        if self.sock:
            try:
                if self.connected:
                    self.debug("resetting...")
                    self._reset()
            except:
                pass
            try:
                self.debug("closing...")
                self.sock.close()
            except:
                pass

    def _scan(self):
        """Find the brain bluetooth device."""
        for addr in bluetooth.discover_devices():
            self.debug('address: %s', addr)
            name = bluetooth.lookup_name(addr)
            self.debug('name: %s', name)
            if name.startswith('Moss'):
                self.address = addr
                return
        raise Exception('No device found')

    def _read(self, n):
        """Read n bytes from self.sock."""
        buf = []
        while n > 0:
            part = self.sock.recv(n)
            buf.append(part)
            n -= len(part)
        return ''.join(buf)

    def _reset(self):
        """Set LED to black (off), set all faces to output mode."""
        self('setLEDState', 0, 0, 0)
        self('setAllFaceStates', *([OUTPUT] * NFACES))
        self('setManyFaceValues', 255, *([127] * NFACES))


def unbuffered(f):
    """Read lines without buffering."""
    chars = []
    while True:
        c = f.read(1)
        if not c:
            break
        chars.append(c)
        if c != '\n':
            continue
        yield ''.join(chars)
        chars = []


def main():
    """Implement a simple STDIO "server".

    Connect to the brain bluetooth device, and then repeatedly read a
    line with a command string and variable number of arguments (values
    in the range of 0-255) send the command to the device and write a
    line with the data of the reply (list of values).
    """
    with Brain(sys.argv) as brain:
        for line in unbuffered(sys.stdin):
            command, sep, data = line.strip().partition(' ')
            data = [int(s) for s in data.split()]
            data = brain(command, *data)
            sys.stdout.write(' '.join(['%d' % i for i in data]) + '\n')


if __name__ == '__main__':
    main()
