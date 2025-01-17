#!/bin/sh

if [ ! -f /data/in/main.py ]; then
    echo "main.py not found!"
    exit 1
fi

mkdir -p /tmp/in
mkdir -p /tmp/out

cp /data/in/main.py /tmp/in/main.py
pyinstaller --onefile /tmp/in/main.py 2> /tmp/out/comp.stderr.txt
cp ./dist/main /data/out/program
