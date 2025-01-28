#!/bin/ash

cp "${IN}/"* /tmp/in

g++ -Wall -o /tmp/out/program /tmp/in/*.cpp 2> /tmp/out/comp.stderr.txt
exit_code=$?

cp /tmp/out/* $OUT

exit $exit_code
