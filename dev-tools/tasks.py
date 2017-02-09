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
    'CURRENT_DIRECTORY': os.path.dirname(os.path.abspath(__file__)),
    'TMP_DIRECTORY': '.tmp',
}

global_vars.update({
    'ROOT': os.path.join(
        global_vars['CURRENT_DIRECTORY'],
        "..",
    ),
    'GOPATH': os.path.join(
        global_vars['CURRENT_DIRECTORY'],
        "..",
        global_vars['TMP_DIRECTORY'],
    ),
    'DEPENDENCIES': os.path.join(
        global_vars['CURRENT_DIRECTORY'],
        'dependencies.txt'
    ),
})

modules = [
    "project"
]

@task
def copy_src(ctx):
    ctx.run(
        "mkdir -p %(GOPATH)s/src/" % global_vars,
        encoding='utf-8'
    )
    ctx.run(
        "rm -rf %(GOPATH)s/src/project" % global_vars,
        encoding='utf-8'
    )
    ctx.run(
        "rm -rf %(GOPATH)s/pkg/" % global_vars,
        encoding='utf-8'
    )
    ctx.run(
        "cp -r %(ROOT)s/src/project %(GOPATH)s/src/project" % global_vars,
        encoding='utf-8'
    )

@task(pre=[copy_src])
def get(ctx):
    with open(global_vars['DEPENDENCIES'], 'r') as f:
        for line in f:
            if len(line) > 0:
                ctx.run(
                    "go get -v %s" % line,
                    encoding='utf-8',
                    env=global_vars
                )

@task(pre=[copy_src])
def run(ctx):
    ctx.run(
        "go run src/project/main.go",
        encoding='utf-8',
        env=global_vars
    )

@task()
def vet(ctx):
    ctx.run(
        "go vet project",
        encoding='utf-8',
        env=global_vars
    )

@task(pre=[copy_src])
def test(
    ctx,
    race=False,
    module='project'
):
    local_command = "go test -v --timeout=10m " % global_vars
    if race:
        local_command += " -race "

    ctx.run(
        "%s %s" % (local_command, module),
        encoding="utf-8",
        env=global_vars
    )

@task(pre=[copy_src])
def build(
    ctx,
    goos='linux',
    goarch='amd64',
    binary_output='./bin/project',
):
    global_vars.update({
        'CGO_ENABLED': '0',
        'GOOS': goos,
        'GOARCH': goarch,
    })
    ctx.run(
        "go build -ldflags '-s' -a -installsuffix cgo -o {} project".format(
            binary_output,
        ),
        encoding="utf-8",
        env=global_vars
    )

