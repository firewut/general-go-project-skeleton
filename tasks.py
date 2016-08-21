# -*- coding: utf-8 -*-
from invoke import task

import multiprocessing
import logging
import socket
import sys
import os

import sys

log = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(logging.INFO)
log.addHandler(out_hdlr)
log.setLevel(logging.INFO)

global_vars = {
    "HOSTNAME": socket.getfqdn(),
    "MODE": "development",
    "COVER_PROFILE_FILE": "/tmp/c.out",
    "CURDIR": os.path.dirname(os.path.abspath(__file__)),
    "VENDOR_DIR": ".vendor",
}

global_vars.update({
    "GOPATH": os.path.join(global_vars["CURDIR"], global_vars["VENDOR_DIR"]),
    "DEPENDENCIES": os.path.join(global_vars["CURDIR"], "dependencies.txt"),
})

GOCOMMAND = """env GOPATH=%(GOPATH)s \
    hostname=%(HOSTNAME)s \
    mode=%(MODE)s """ % global_vars

global_vars.update({
    "GOCOMMAND": GOCOMMAND,
})

modules = [
    "project"
]

@task
def remove_deps(ctx):
    ctx.run("rm -rf %(GOPATH)s" % global_vars, encoding="utf-8")

@task
def copy_src(ctx):
    ctx.run("mkdir -p %(GOPATH)s" % global_vars, encoding="utf-8")
    ctx.run("rm -rf %(GOPATH)s/src/project" % global_vars, encoding="utf-8")
    ctx.run("rm -rf %(GOPATH)s/pkg/" % global_vars, encoding="utf-8")
    ctx.run("cp -r %(CURDIR)s/src %(GOPATH)s" % global_vars, encoding="utf-8")

@task(pre=[remove_deps, copy_src])
def get(ctx, install=True):
    if install:
        with open(global_vars["DEPENDENCIES"], 'r') as f:
            for line in f:
                local_command = "env GOPATH=%(GOPATH)s" % global_vars
                ctx.run("%s go get -v %s" % (local_command, line), encoding="utf-8")


@task(pre=[copy_src])
def start_fast(ctx, race=False):
    local_command = "%(GOCOMMAND)s go run %(GOPATH)s/src/project/main.go" % global_vars
    if race:
        local_command += " -race "
    ctx.run(local_command, encoding="utf-8")


@task(pre=[get, copy_src])
def start(ctx):
    ctx.run("%(GOCOMMAND)s go run %(GOPATH)s/src/project/main.go" %
        global_vars, encoding="utf-8")


@task(pre=[copy_src])
def test_fast(ctx, module="", race=False, cover=False, report=False, count=1, cpu=0):
    if cpu == 0:
        cpu = multiprocessing.cpu_count()

    if module in modules:
        local_command = "time %(GOCOMMAND)s go test -v " % global_vars
        if race:
            local_command += " -race "
        if cover:
            local_command += " -coverprofile %s" % global_vars[
                "COVER_PROFILE_FILE"]
        local_command += " -count=%d -cpu=%d --parallel %d" % (count, cpu, cpu)

        ctx.run("%s %s" % (local_command, module), encoding="utf-8")

        if report:
            ctx.run("%s go tool cover -html=%s" %
                (global_vars["GOCOMMAND"], global_vars["COVER_PROFILE_FILE"]), encoding="utf-8")
    else:
        log.error("module %s is not registered" % module)


@task(pre=[copy_src])
def vet(ctx):
    for module in modules:
        local_command = "%(GOCOMMAND)s go vet " % global_vars
        log.info("Checking %s" % module)
        ctx.run("%s %s" % (local_command, module), encoding="utf-8")


@task(pre=[copy_src])
def build(ctx):
    ctx.run("env CGO_ENABLED=0 GOOS=linux GOARCH=amd64 GOPATH=%(GOPATH)s go build \
            -ldflags '-s' -a -installsuffix cgo -o ./bin/project %(GOPATH)s/src/project/main.go" % global_vars
    )
