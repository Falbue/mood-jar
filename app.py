# app.py
from flask import Flask, render_template
import atexit
import os
import signal

def cleanup():
    pid = os.getpid()
    os.kill(pid, signal.SIGTERM)

atexit.register(cleanup)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
