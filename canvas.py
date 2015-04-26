# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import random
import time

import zmq


class Bandit(object):
    def __init__(self, data, index):
        self.data = data
        self.index = index
        self.count = 1


random_colors = [
    Bandit(random.randrange(2 ** 24), i) for i in range(8)
]


def randcolor():
    """Returns random color according to probability of success."""
    total_colors = sum((c.count for c in random_colors))
    random_count = random.randrange(total_colors)
    running_total = 0
    for c in random_colors:
        running_total += c.count
        if random_count < running_total:
            return c
    print "Warning, got unexpected random_count"
    return random_colors[-1]


def rgbcolor(value):
    """Returns RGB color value from 24-bit integer."""
    r = (value & 0xFF0000) >> 16
    g = (value & 0xFF00) >> 8
    b = value & 0xFF
    return (r, g, b)


def main():
    """Example of how to send server generated events to clients."""
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind('tcp://127.0.0.1:5001')
    while True:
        color = randcolor()
        print "sending color ", color.data
        socket.send(repr(color.data))
        time.sleep(1)


if __name__ == '__main__':
    main()
