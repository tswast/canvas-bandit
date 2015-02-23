# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from gevent import monkey
monkey.patch_all()

import random
import time
from threading import Thread
from flask import Flask, render_template, session, request
from flask.ext.socketio import SocketIO, emit, join_room, leave_room, \
        close_room, disconnect

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
thread = None


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


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        time.sleep(1)
        count += 1
        color = randcolor()
        socketio.emit(
            'my response',
            {
                'data': 'Server generated event : color {0} count {1}'.format(color.index, color.count),
                'color': 'rgb({0}, {1}, {2})'.format(*rgbcolor(color.data)),
                'count': count,
                'index': color.index,
            },
            namespace='/test')


@app.route('/')
def index():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.start()
    return render_template('index.html')


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


@socketio.on('my event', namespace='/test')
def test_message(message):
    print 'got: ', message
    try:
        random_colors[int(message['index'])].count += 1
    except KeyError:
        pass


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
