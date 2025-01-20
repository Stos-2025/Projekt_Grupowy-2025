#!/bin/sh

if [ ! -f /data/in/main.py ]; then
    echo "main.py not found!"
    exit 1
fi

cp /data/in/*.py /tmp/in
pyinstaller --onefile --distpath /tmp/out -n program /tmp/in/main.py 2> /tmp/out/comp.stderr.txt #todo change pyinstaller
exit_code=$?

cp /tmp/out/* /data/out
# cp ./dist/* /data/out

exit $exit_code
