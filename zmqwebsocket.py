# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import random

from gevent import joinall, pywsgi, sleep, spawn
from geventwebsocket.handler import WebSocketHandler
import zmq.green as zmq



def rgbcolor(value):
    """Returns RGB color value from 24-bit integer."""
    r = (value & 0xFF0000) >> 16
    g = (value & 0xFF00) >> 8
    b = value & 0xFF
    return (r, g, b)



def send(ws, socket):
    print "Calling send"
    count = 0
    while True:
        msg = socket.recv()
        color = 'rgb({0}, {1}, {2})'.format(*rgbcolor(int(msg)))
        count += 1
        #print 'sending color: ', color
        ws.send(json.dumps(
            {
                'data': 'Server generated event',
                'color': color,
                'count': count
            }))
        #print 'done sending color: ', color



def receive(ws):
    print "Calling receive"
    while True:
        message = ws.receive()
        #print "got message", message



class WebSocketApp(object):
    '''Send random data to the websocket'''

    def __call__(self, environ, start_response):
        ws = environ['wsgi.websocket']
        context = zmq.Context()
        socket = context.socket(zmq.PAIR)
        socket.connect('tcp://127.0.0.1:5001')

        s = spawn(send, ws, socket)
        r = spawn(receive, ws)
        joinall([s, r])



server = pywsgi.WSGIServer(("", 10000), WebSocketApp(),
    handler_class=WebSocketHandler)
server.serve_forever()
