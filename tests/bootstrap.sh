#!/bin/bash

if ! [ -x bin/casperjs ]; then
    python2.7 bootstrap.py
    bin/buildout install casperjs
fi
