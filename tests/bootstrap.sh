#!/bin/bash

python -c "import os; print(os.uname())"

if ! [ -x bin/casperjs ]; then
    python2.7 bootstrap.py -d
    bin/buildout install casperjs
fi
