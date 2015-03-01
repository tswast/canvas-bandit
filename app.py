# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import gevent
from gevent import monkey
monkey.patch_all()

import random
from flask import Flask, render_template, session, request
from flask.ext.socketio import SocketIO, emit, join_room, leave_room, \
        close_room, disconnect
import zmq.green as zmq

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
thread = None


def rgbcolor(value):
    """Returns RGB color value from 24-bit integer."""
    r = (value & 0xFF0000) >> 16
    g = (value & 0xFF00) >> 8
    b = value & 0xFF
    return (r, g, b)


def background_thread():
    """Example of how to send server generated events to clients."""
    # TODO: launch canvas.py
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.connect('tcp://127.0.0.1:5001')
    count = 0
    while True:
        msg = socket.recv()
        color = 'rgb({0}, {1}, {2})'.format(*rgbcolor(int(msg)))
        count += 1
        print 'sending color: ', color
        socketio.emit(
            'my response',
            {
                'data': 'Server generated event',
                'color': color,
                'count': count
            },
            namespace='/test')
        print 'done sending color: ', color


@app.route('/')
def index():
    print 'render index'
    return render_template('index.html')


@socketio.on('connect', namespace='/test')
def test_connect():
    print 'connect'
    global thread
    if thread is None:
        thread = gevent.spawn(background_thread)
    emit('my response', {'data': 'Connected', 'count': 0})


@socketio.on('my event', namespace='/test')
def test_message(message):
    print 'got: ', message
    # TODO: send positive reinforcement message


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
