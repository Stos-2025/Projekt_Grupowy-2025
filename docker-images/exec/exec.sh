#!/bin/sh

start_process() {
    input_file="$1"
    output_file="/tmp/out/$(basename "$input_file" ".in").stdout.out"
    error_file="/tmp/out/$(basename "$input_file" ".in").stderr.out"
    
    
    prlimit --cpu=2 --as=104857600 --nofile=64 -- \
        time -v -o /tmp/out/$(basename "$input_file" ".in").time.out /tmp/in/program < "$input_file"   2> "$error_file"  | cat   
}

if [ ! -x /data/in/program ]; then
    echo "Binary not found or not executable: $binary_path"
    exit 1
fi

mkdir -p /tmp/in
mkdir -p /tmp/out
cp /data/in/program /tmp/in

for input_file in /data/in/*.in; do
    start_process "$input_file"
done

cp /tmp/out/* /data/out






