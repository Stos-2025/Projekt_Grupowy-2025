#!/bin/ash

cp "${INPUT}/"* /tmp/in

g++ -Wall -o /tmp/out/program /tmp/in/*.cpp 2> /tmp/out/comp.stderr.txt
exit_code=$?

cp /tmp/out/* $OUTPUT

exit $exit_code
