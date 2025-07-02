import json
import os
from typing import Tuple

def check_answer(answer_path: str, input_path: str) -> Tuple[bool, str]:
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
    with open(exec_path, "r") as exec_file:
        exec = json.load(exec_file)
        if exec["return_code"] > 0:
            return False, f"program exited with return code {exec['return_code']}"
        elif exec["return_code"] < 0:
            return False, f"program was killed with signal {exec['return_code']}"
        # if exec["user_time"] > 2:
        #     return False, f"program took too long: {exec['user_time']}s"
        # if exec["memory"] > 1000000:
        #     return False, f"program used too much memory: {exec['memory']}kb" 
    return True, "ok"

def check_comp(comp_path: str) -> Tuple[bool, str]:
    try:
        with open(comp_path, "r") as comp_file:
            comp = json.load(comp_file)
            if comp["return_code"] != 0:
                return False, f"compilation failed with return code {comp['return_code']}"
    except Exception as e:
        pass
    return True, "ok"

def check(name: str):          
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
        