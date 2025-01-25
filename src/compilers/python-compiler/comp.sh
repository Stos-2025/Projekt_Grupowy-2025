#!/bin/sh

if [ ! -f /data/in/main.py ]; then
    echo "main.py not found!"
    exit 1
fi

cp "${INPUT}/"* /tmp/in

pyinstaller --onefile --distpath /tmp/out -n program /tmp/in/main.py 2> /tmp/out/comp.stderr.txt #todo change pyinstaller
exit_code=$?

cp /tmp/out/* $OUTPUT

exit $exit_code
