#!/bin/sh

if [ ! -f /data/in/main.rs ]; then
    echo "main.rs not found!"
    exit 1
fi

mkdir -p /tmp/in
mkdir -p /tmp/out

cp /data/in/main.rs /tmp/in/main.rs
rustc -o /tmp/out/program /tmp/in/main.rs 2> /tmp/out/comp.stderr.txt
cp /tmp/out/* /data/out/
