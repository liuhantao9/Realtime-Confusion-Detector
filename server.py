from flask import Flask, jsonify, render_template, request
from subprocess import call
from flask_socketio import SocketIO, send, emit
from datetime import datetime
import random as r

DATE_FMT = "%Y-%m-%d %H:%M:%S"

app = Flask(__name__)
app.secret_key = 'mysecret'
socket_io = SocketIO(app)

_mode = 'stop'

@app.route('/')
def welcome():
    return render_template('index.html')

@app.route('/charts', methods=['POST'])
def draw():
    if request.method == 'POST':
        return render_template('charts.html', x_window=100)

# Receiving Messages
@socket_io.on('my_event')
def drawer(data):
    global _mode
    if _mode == 'stop':
        pass
    else:
        print('input data: ' + str(data))
        socket_io.emit('update', data)

@socket_io.on('my_ping')
def ping_pong():
    emit('my_pong')

@socket_io.on('change mode')
def changer(data):
    global _mode
    if data['mode'] == 'start':
        _mode = 'start'
    else:
        _mode = 'stop'

if __name__ == '__main__':
    socket_io.run(app, debug=True, host='localhost', port=8000)
    #socket_io.run(app, debug=True, host='0.0.0.0', port=80)
