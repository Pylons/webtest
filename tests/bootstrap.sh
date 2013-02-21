#!/bin/bash

if [ -d parts/casperjs/n1k0-casperjs-9b9fb4b ]; then
  rm -Rf bin/casperjs parts/casperjs/
fi

if [ -x bin/casperjs ]; then
  bin/casperjs | grep "CasperJS version 1.0" || rm -Rf bin/casperjs parts/casperjs/
fi

if ! [ -x bin/casperjs ]; then
    python2.7 bootstrap.py
    bin/buildout install casperjs
fi

chmod +x parts/casperjs/*/bin/*js

file parts/casperjs/phantomjs*/bin/phantomjs

python -c "import os; print(os.uname())"
