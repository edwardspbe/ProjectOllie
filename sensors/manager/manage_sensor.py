from flask import Flask, redirect, url_for, render_template, request
from subprocess import Popen, PIPE, STDOUT
from lxml import html
import os
import json

BASE='/opt/ollie/monitor'
conf='/opt/ollie/monitor/ollie_at_your_service.conf'

app = Flask(__name__)


def get_conf():
    confdata = []
    with open(conf) as json_data_file:
        confdata = json.load(json_data_file)
    return confdata

def update_conf(threshold, delay):
    confdata = []
    with open(conf) as json_data_file:
        confdata = json.load(json_data_file)
    confdata['sensor_threshold'] = threshold
    confdata['notif_delay'] = delay
    with open(conf, 'w') as outfile:
        json.dump(confdata, outfile) 
    return confdata

def get_status():
    cmd = "%s/status.bash" % BASE
    state = 0
    status = ''
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    (value, err) = p.communicate()
    if "running" in str(value):
        status += "<h2>Sensor running... </h2>"
        state=1
    else :
        status += "<h2>Sensor is not currently running</h2>\n"
    status += "<p>%s</p>" % value.decode("utf-8") 
    return state,status


@app.route('/stop', methods=['POST'])
def stop():
    cmd = "%s/state.bash off" % BASE
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    (value, err) = p.communicate()
    return render_template("index.html", status=get_status())


@app.route('/start', methods=['POST'])
def start():
    cmd = "%s/state.bash on" % BASE
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    (value, err) = p.communicate()
    return render_template("index.html", status=get_status())

@app.route('/chgstate', methods=['GET', 'POST'])
def chgstate():
    if request.method == 'POST':
        #action = request.form['action']
        threshold = request.form['threshold']
        delay = request.form['delay']
        confdata = update_conf(threshold, delay)
    else:
        confdata = get_conf()
    return render_template("chgstate.html", status=get_status(), confdata=confdata)

@app.route("/")
def home():
    return render_template("index.html", status=get_status())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
