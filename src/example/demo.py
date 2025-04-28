import subprocess
import os
import time
import json
from typing import Tuple

def print_resoults(path: str) -> Tuple[int, str]:
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

def run_example(build: bool = True, compile: bool=True, logs: bool=True):
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
    run_example()