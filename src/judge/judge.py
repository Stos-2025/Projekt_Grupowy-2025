"""
Judge module for evaluating program output against expected results.

This module provides functions to check compilation results, execution results,
and compare program output with expected answers in a competitive programming
judge system.

Functions:
    check_answer: Compare program output with expected answer
    check_exec: Validate program execution results
    check_comp: Validate compilation results
    check: Main function to perform complete evaluation
"""

import json
import os
from typing import Tuple


def check_answer(answer_path: str, input_path: str) -> Tuple[bool, str]:
    """
    Compare program output with expected answer line by line.

    This function reads two files and compares their content line by line,
    ignoring leading and trailing whitespace. It's used to determine if
    a program's output matches the expected answer.

    Args:
        answer_path (str): Path to the file containing expected answer
        input_path (str): Path to the file containing program output

    Returns:
        Tuple[bool, str]: A tuple containing:
            - bool: True if output matches expected answer, False otherwise
            - str: Descriptive message about the comparison result

    Raises:
        FileNotFoundError: If either input file doesn't exist
        PermissionError: If files cannot be read due to permissions
        UnicodeDecodeError: If files contain invalid UTF-8 content

    Example:
        >>> result, info = check_answer("expected.txt", "output.txt")
        >>> if result:
        ...     print("Output is correct!")
        ... else:
        ...     print(f"Output is incorrect: {info}")
    """
    info = "ok"
    line_nr = 0
    with open(answer_path, "r") as answer, open(input_path, "r") as input:
        for line in answer:
            line_nr += 1
            try:
                output_line = input.readline()
            except EOFError:
                info = f"unexpected EOF in line {line_nr}"
                return (False, info)
            if line.strip() != output_line.strip():
                info = f"line {line_nr} is not correct: expected {line.strip()} but got {output_line.strip()}"
                return (False, info)
        #probably the output can be longer than the answer but its only example 
    return (True, info)

def check_exec(exec_path: str) -> Tuple[bool, str]:
    """
    Validate program execution results from execution metadata.

    This function checks if a program executed successfully by examining
    the execution metadata JSON file. It verifies the return code and
    can be extended to check execution time and memory usage limits.

    Args:
        exec_path (str): Path to the JSON file containing execution metadata

    Returns:
        Tuple[bool, str]: A tuple containing:
            - bool: True if execution was successful, False otherwise
            - str: Descriptive message about the execution result

    Raises:
        FileNotFoundError: If the execution metadata file doesn't exist
        json.JSONDecodeError: If the JSON file is malformed
        KeyError: If required fields are missing from the JSON

    Example:
        >>> result, info = check_exec("program.exec.json")
        >>> if result:
        ...     print("Program executed successfully")
        ... else:
        ...     print(f"Program execution failed: {info}")
    """
    with open(exec_path, "r") as exec_file:
        exec = json.load(exec_file)
        if exec["return_code"] != 0:
            return False, f"program exited with return code {exec['return_code']}"
        # if exec["user_time"] > 2:
        #     return False, f"program took too long: {exec['user_time']}s"
        # if exec["memory"] > 1000000:
        #     return False, f"program used too much memory: {exec['memory']}kb" 
    return True, "ok"

def check_comp(comp_path: str) -> Tuple[bool, str]:
    """
    Validate compilation results from compilation metadata.

    This function checks if a program compiled successfully by examining
    the compilation metadata JSON file. It's designed to be resilient
    to missing or malformed files, returning success in case of any
    errors (fail-open behavior).

    Args:
        comp_path (str): Path to the JSON file containing compilation metadata

    Returns:
        Tuple[bool, str]: A tuple containing:
            - bool: True if compilation was successful or file is missing/malformed, False if compilation failed
            - str: Descriptive message about the compilation result

    Note:
        This function implements fail-open behavior - if the compilation
        metadata file is missing or cannot be parsed, it returns success.
        Only explicit compilation failures (return_code != 0) are treated as errors.

    Example:
        >>> result, info = check_comp("program.comp.json")
        >>> if result:
        ...     print("Compilation successful or no compilation errors detected")
        ... else:
        ...     print(f"Compilation failed: {info}")
    """
    try:
        with open(comp_path, "r") as comp_file:
            comp = json.load(comp_file)
            if comp["return_code"] != 0:
                return False, f"compilation failed with return code {comp['return_code']}"
    except Exception as e:
        pass
    return True, "ok"

def check(name: str) -> None:
    """
    Perform complete evaluation of a program submission.

    This function orchestrates the complete evaluation process for a program
    submission. It checks compilation results, execution results, and compares
    the program output with expected answers. The final result is written to
    a JSON file.

    The evaluation process follows these steps:
    1. Check compilation results
    2. If compilation succeeded, check execution results
    3. If execution succeeded, check answer correctness
    4. Generate final grade (1 for success, 0 for failure)
    5. Write results to judge JSON file

    Args:
        name (str): Base name of the test case (without file extension)

    Environment Variables:
        ANS (str): Directory path containing expected answer files
        IN (str): Directory path containing program output files
        OUT (str): Directory path for writing judge results

    Files Used:
        - {ANS}/{name}.out: Expected answer file
        - {IN}/{name}.stdout.out: Program output file
        - {OUT}/comp.json: Compilation metadata
        - {OUT}/{name}.exec.json: Execution metadata
        - {OUT}/{name}.judge.json: Judge results (created)

    Raises:
        TypeError: If required environment variables are not set
        FileNotFoundError: If required input files don't exist
        json.JSONDecodeError: If metadata files are malformed
        PermissionError: If files cannot be read or written

    Example:
        >>> os.environ['ANS'] = '/path/to/answers'
        >>> os.environ['IN'] = '/path/to/outputs'
        >>> os.environ['OUT'] = '/path/to/results'
        >>> check("test1")  # Evaluates test case "test1"
    """          
    answer_path = os.getenv('ANS')+f"/{name}.out"
    input_path = os.getenv('IN')+f"/{name}.stdout.out"
    comp_path = os.getenv('OUT')+f"/comp.json"
    exec_path = os.getenv('OUT')+f"/{name}.exec.json"

    output = {}
    is_correct, info = check_comp(comp_path)
    if is_correct:
        is_correct, info = check_exec(exec_path)
    if is_correct:
        is_correct, info = check_answer(answer_path, input_path)
    
    output["grade"] = 1 if is_correct else 0
    output["info"] = info
    with open(f"{os.getenv('OUT')}/{name}.judge.json", "w") as judge_file:
        json.dump(output, judge_file)
        