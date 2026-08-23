#!/bin/bash

VENV="/var/www/lafayette/.venv"

if [ ! -x "$VENV/bin/python" ]; then
    echo "Lafayette: repairing virtual environment Python launcher"
    /usr/bin/python3 -m venv --upgrade "$VENV"
fi

if [ ! -x "$VENV/bin/python" ]; then
    echo "Lafayette: virtual environment repair failed"
    exit 1
fi

exit 0
