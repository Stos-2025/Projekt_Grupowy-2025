"""
Execution module for running compiled programs in isolated environment.

This module provides functionality to execute compiled programs with resource limits,
capture their output, and collect execution statistics. It's designed to run in a
containerized environment with proper sandboxing.

This script expects one command-line argument: the test case name (without extension).
It reads environment variables to determine file locations and executes the program
with the specified input, capturing output and metadata.

Environment Variables:
    BIN: Directory containing the compiled program binary
    IN: Directory containing input files (.in)
    STD: Directory for standard output/error files
    OUT: Directory for execution metadata (.exec.json)

Usage:
    python exec.py <test_name>

Example:
    python exec.py test1
    # Executes program with test1.in as input
    # Creates test1.stdout.out, test1.stderr.out, test1.exec.json
"""

import sys
import subprocess
import resource
import json
import os
# import psutil

name = sys.argv[1]  

binary_path = f"{os.getenv('BIN')}/program"
input_path=f"{os.getenv('IN')}/{name}.in"

output_path=f"{os.getenv('STD')}/{name}.stdout.out"
# output_path=f"/tmp/out/{name}.stdout.out"
error_path=f"{os.getenv('STD')}/{name}.stderr.out"
# error_path=f"/tmp/out/{name}.stderr.out"
exec_path=f"{os.getenv('OUT')}/{name}.exec.json"
# exec_path=f"/tmp/out/{name}.exec.json"

return_code = 0
with open(input_path, "r") as input_file, open(error_path, "w") as error_file, open(exec_path, "w") as exec_file, open(output_path, "w") as output_file:
    program_process = subprocess.Popen(
        [binary_path],
        stdin=input_file,    
        stderr=error_file,
        stdout=output_file,
    )

    resource.prlimit(program_process.pid, resource.RLIMIT_CPU, (2, 2)) #todo change
    program_process.wait()

    meta = {}
    resources = resource.getrusage(resource.RUSAGE_CHILDREN)
    meta["return_code"] = program_process.returncode
    meta["user_time"] =  round(resources.ru_utime, 10)
    meta["memory"] =  round(resources.ru_maxrss, 10)
    json.dump(meta, exec_file)
