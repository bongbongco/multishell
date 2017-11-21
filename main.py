# -*- coding: utf-8 -*-

from flask import Flask, render_template, request
from flask_paginate import Pagination
import paramiko
from multiprocessing import Pool, Manager
import webbrowser
from functools import partial

app = Flask(__name__)


def LinuxProcess(connect_data, hostname):
    user = connect_data[0]
    pw = connect_data[1]
    exec_command = connect_data[2]

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=user, password=pw)
    stdin, stdout, stderr = ssh.exec_command(exec_command)
    return {'host':hostname, 'result':stdout.read().replace('\n', '<br />')}


@app.route("/upload", methods=['POST'])
def uploadtest(error=None):
    print 'test'


@app.route("/command", methods=['POST'])
def command(error=None):
    workerManager = Manager()
    connect_data = workerManager.list([request.form['username'],
                                       request.form['password'],
                                       request.form['command']])
    LinuxProcess_connectData = partial(LinuxProcess, connect_data)

    pool = Pool(len(request.form['iplist'].split(',')))

    try:
        commandResults = pool.map(LinuxProcess_connectData, request.form['iplist'].split(','))
    except:
        error = "Fail Excute Command"

    pool.close()
    pool.join()

    commandPagination = Pagination(
        css_framework='bootstrap4',
        link_size='sm',
        show_single_page=False,
        page=1,
        per_page=10,
        total=len(commandResults),
        href="page?resultPage={0}",
        record_name='commandResults',
        format_total=True,
        format_number=True,)


    return render_template('home.html',
                           commandResults=commandResults,
                           commandPagination=commandPagination,
                           id=request.form['username'],
                           password=request.form['password'],
                           hosts=request.form['iplist'],
                           error=error)


@app.route("/")
def home():
    return render_template("home.html")


def Run():
    webbrowser.open('http://127.0.0.1:5000')


if __name__ == '__main__':
    #Run()
    app.run()