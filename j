#!/bin/bash

python=$(which python2.7)
judge=judge/main.py

if [ -z "$python" ]; then
    echo "ERROR: python2.7 no parece estar instalado!"
else
    eval $python $judge "$@"
fi
