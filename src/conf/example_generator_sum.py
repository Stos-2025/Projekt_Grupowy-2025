#!/usr/bin/env python3
"""
Sum Test Data Generator for Competitive Programming Judge System.

This script generates test data for sum problems where the task is to sum a series
of numbers. It creates input files containing a number n followed by n lines of "1",
and output files containing the expected sum (which equals n).

The generator creates test cases with exponentially increasing input sizes using
the formula n = round(2.3^i), creating challenging test cases for performance testing.

Test Case Structure:
- Input: First line contains n, followed by n lines each containing "1"
- Output: Single line containing the sum (equals n)

Special Cases:
- Test case 10 has a deliberately wrong expected output ("67") for testing
  the judge's ability to detect incorrect answers

Directory Structure:
- src/example/exec-in/in/: Input files (*.in)
- src/example/exec-in/out/: Expected output files (*.out)
- src/example/comp-out/: Compilation output directory
- src/example/exec-out/: Execution output directory

Usage:
    python example_generator_sum.py
    # Creates 22 test cases (0.in to 21.in and corresponding .out files)
"""

import os
import shutil

file_dir = os.path.dirname( os.path.abspath(__file__) )
os.chdir(f"{file_dir}/../..")

exec_in_path = "src/example/exec-in/"
comp_out_path = "src/example/comp-out"
exec_out_path = "src/example/exec-out"

if os.path.exists(comp_out_path):
    shutil.rmtree(comp_out_path)
os.makedirs(comp_out_path)

if os.path.exists(exec_out_path):
    shutil.rmtree(exec_out_path)
os.makedirs(exec_out_path)

if os.path.exists(exec_in_path):
    shutil.rmtree(exec_in_path)
os.makedirs(exec_in_path)
os.makedirs(exec_in_path+"in")
os.makedirs(exec_in_path+"out")

for i in range(22):
    in_file_name = f"{exec_in_path}in/{i}.in"
    out_file_name = f"{exec_in_path}out/{i}.out"
    
    in_test_data = ""
    out_test_data = ""
    # n = 20000000//(20-i)
    n = round(2.3**i)
    print(n)

    with open(in_file_name, 'a') as file:
        file.write(f"{n}\n")
        for j in range(n):
            file.write("1\n")

    out_test_data += f"{n}\n"
    with open(out_file_name, 'w') as file:
        file.write(out_test_data if i != 10 else "67")
    
    os.chmod(in_file_name, 0o777)
    os.chmod(out_file_name, 0o777)
    os.chmod(comp_out_path, 0o777)
    os.chmod(exec_out_path, 0o777)
    os.chmod(exec_in_path, 0o777)

