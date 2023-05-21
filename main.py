#!/usr/bin/env python3
from webapp import *
from flask_socketio import SocketIO, emit

app = initialise()
socket = SocketIO(app)

@socket.on('message_sent', namespace='/chat-page')
def text(payload):
    emit('message_received', payload, broadcast=True)

if __name__ == "__main__":
    socket.run(app, host="0.0.0.0", port=8081, debug=True, ssl_context=("certs/server.crt", "certs/server.key"))