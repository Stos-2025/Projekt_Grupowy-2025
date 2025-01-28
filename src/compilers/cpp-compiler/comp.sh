#!/bin/ash

cp "${SRC}/"* /tmp/src

g++ -Wall -o /tmp/bin/program /tmp/src/*.cpp 2> /tmp/out/comp.txt
exit_code=$?

cp -u /tmp/out/* "${OUT}"
cp /tmp/bin/* "${BIN}"

exit $exit_code