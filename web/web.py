#!/usr/bin/env python

import settings_web
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=settings_web.listen_port, host=settings_web.listen_host)
