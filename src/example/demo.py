#!/usr/bin/env python3
"""
Demo System for Competitive Programming Judge Pipeline.

This module provides a complete demonstration of the competitive programming
judge system, including compilation, execution, and evaluation phases.
It orchestrates Docker containers for each phase and provides formatted
output of test results.

The demo system supports:
- Building Docker images for compilation, execution, and judging
- Running the complete pipeline on test cases
- Measuring execution times for performance analysis
- Formatted output with color-coded results
- Configurable logging and build options

Functions:
    print_resoults: Format and display test results in a table
    run_example: Execute the complete judge pipeline

Usage:
    python demo.py
    # Runs the complete demo with default settings
    
    Or import and use functions:
    from demo import run_example, print_resoults
    run_example(build=True, compile=True, logs=True)
"""

import subprocess
import os
import time
import json
from typing import Tuple

def print_resoults(path: str) -> Tuple[int, str]:
    """
    Format and display test execution results in a table.

    This function reads execution and judging results from JSON files,
    formats them into a color-coded table, and calculates the total
    points scored. It handles sorting of test cases and provides
    visual feedback for different result types.

    Args:
        path (str): Directory path containing .exec.json and .judge.json files

    Returns:
        Tuple[int, str]: A tuple containing:
            - int: Total points scored (number of successful test cases)
            - str: Formatted table string with colored results

    Color Coding:
        - Green (65): Successful test case
        - Red (131): Failed test case
        - Orange (173): Runtime error (non-zero return code)

    Example:
        >>> points, result = print_resoults("./results")
        >>> print(result)
        +----+------+-----+
        | nr | time | ret |
        +----+------+-----+
        |  0 | 0.12 |   0 | ok
        |  1 | 0.25 |   1 | wrong answer
        +----+------+-----+
        | points: 1       |
        +----+------+-----+
    """
    ret = ""
    ret += "+----+------+-----+\n"
    ret += "| nr | time | ret |\n"
    ret += "+----+------+-----+\n"
    points = 0

    tests = []
    for file in os.listdir("./src/example/exec-out"):
        if file.endswith('.judge.json'):
            tests.append(int(file.split('.')[0]))
    tests.sort()
    for test in tests:
        with open(f"{path}/{test}.exec.json", "r") as exec_file, open(f"{path}/{test}.judge.json", "r") as judge_file:
            exec = json.load(exec_file)
            judge = json.load(judge_file)
            color = 131 
            if judge["grade"]:
                points += 1
                color = 65
            if exec["return_code"]!=0:
                color = 173
            ret += f'|\033[48;5;{color}m\033[38;5;232m {test:>2} | {exec["user_time"]:.2f} | {exec["return_code"]:>3} \033[0m| {judge["info"]}\n'
    ret += "+----+------+-----+\n"
    ret += "| "+f"points: {points}".center(15)+" |\n"
    ret += "+----+------+-----+"
    return points, ret

def run_example(build: bool = True, compile: bool=True, logs: bool=True) -> None:
    """
    Execute the complete competitive programming judge pipeline.

    This function orchestrates the entire judging process including:
    1. Building Docker images (optional)
    2. Compiling source code
    3. Executing test cases
    4. Evaluating results
    5. Displaying formatted results

    The function configures Docker commands with appropriate security settings,
    resource limits, and volume mounts for isolated execution.

    Args:
        build (bool): Whether to build Docker images before running (default: True)
        compile (bool): Whether to compile source code (default: True)
        logs (bool): Whether to enable debug logging (default: True)

    Docker Configuration:
        - Resource limits: 30 second CPU limit
        - Network isolation: --network none
        - Security: --security-opt no-new-privileges
        - Volume mounts: Read-only input, writable output

    Pipeline Phases:
        1. Compilation: Compiles source code using cpp-compiler
        2. Execution: Runs compiled program with test inputs
        3. Judging: Evaluates output against expected results

    Environment Variables:
        - BIN: Binary output directory
        - LOGS: Logging level (on/off)

    Example:
        >>> run_example(build=True, compile=True, logs=True)
        >Compilation time: 2.34
        >Execution time: 1.56
        >Judge time: 0.78
        [Results table displayed]
        
        >>> run_example(build=False, compile=False, logs=False)
        # Runs only execution and judging phases without building
    """
    # build = False
    # logs = False
    exmp_path = r"./src/example"
    comp_path = r"./src/compilers/cpp-compiler"
    # comp_path = r"./src/compilers/python-compiler"
    exec_path = r"./src/exec-python"
    judge_path = r"./src/judge"

    exec_in = exmp_path+"/exec-in"
    exec_out = exmp_path+"/exec-out"
    comp_in = exmp_path+"/comp-in"
    comp_out = exmp_path+"/comp-out" 

    run_comp_command = [
        "docker", "run", 
        "--rm",
        # "--cpus=1.0",
        "--ulimit", "cpu=30:30",
        "--network", "none",
        "--security-opt", "no-new-privileges",
        "-e",
        "BIN=/data/out",
        "-v", f"{comp_in}:/data/in:ro",
        "-v", f"{comp_out}:/data/out",
        "comp"
    ]
    run_exec_command = [
        "docker", "run", 
        "--rm",
        # "--cpus=0.5",
        "--ulimit", "cpu=30:30",
        "--network", "none",
        "--security-opt", "no-new-privileges",
        "-e",
        f"LOGS={'on' if logs else 'off'}",
        "-v", f"{exec_in}/in:/data/in:ro",
        "-v", f"{comp_out}:/data/bin:ro",
        "-v", f"{exec_out}:/data/out",
        "exec"
    ]
    run_judge_command = [  
        "docker", "run", 
        "--rm",
        # "--cpus=0.5",
        "--ulimit", "cpu=30:30",
        "--network", "none",
        "--security-opt", "no-new-privileges",
        "-e",
        f"LOGS={'on' if logs else 'off'}",
        "-v", f"{exec_out}:/data/in:ro",
        "-v", f"{exec_out}:/data/out",
        "-v", f"{exec_in}/out:/data/answer:ro",
        "judge"
    ]


    #building
    
    if build:
        subprocess.run(["docker", "build", "--build-arg", f"LOGS={'on' if logs else 'off'}", "-t", "exec", exec_path], check=True)
        subprocess.run(["docker", "build", "--build-arg", f"LOGS={'on' if logs else 'off'}", "-t", "judge", judge_path], check=True)
        subprocess.run(["docker", "build", "-t", "comp", comp_path], check=True)


    #compiling
    
    if compile:
        start_time = time.time()
        
        try:
            subprocess.run(run_comp_command, check=True)
        except Exception as e:
            print(e)
            return 1

        print(f">Compilation time: {round(time.time() - start_time, 2)}")



    #running
    
    start_time = time.time()
    
    try:
        subprocess.run(run_exec_command, check=True)
    except Exception as e:
        print(e)
        return 1
    
    print(f">Execution time: {round(time.time() - start_time, 2)}")


    #judging

    start_time = time.time()
    
    try:
        subprocess.run(run_judge_command, check=True)
    except Exception as e:
        print(e)
        return 1
    
    print(f">Judge time: {round(time.time() - start_time, 2)}")

    #printing resoults
    
    points, result = print_resoults(exec_out)
    print(result)


if __name__ == "__main__":
    file_dir = os.path.dirname( os.path.abspath(__file__) )
    os.chdir(f"{file_dir}/../..")
    os.system("ls")
    run_example()