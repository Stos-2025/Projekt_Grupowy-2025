#!/usr/bin/env python3

import subprocess
import os
import time
import json
import dotenv
import argparse
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

def run_example(build: bool = True, compile: bool=True, logs: bool=True, push: bool=False) -> None:
    exec_image = os.getenv(r"EXEC_IMAGE_NAME") or "exec"
    comp_image = os.getenv(r"GPP_COMP_IMAGE_NAME") or "gpp_comp"
    # comp_image = os.getenv(r"PY3_COMP_IMAGE_NAME") or "py3_comp"
    judge_image = os.getenv(r"JUDGE_IMAGE_NAME") or "judge"
    
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
    MAINFILE = "main.py"

    run_comp_command = [
        "docker", "run", 
        "--rm",
        # "--cpus=1.0",
        "--ulimit", "cpu=30:30",
        "--network", "none",
        "--security-opt", "no-new-privileges",
        "-e",
        "BIN=/data/out",
        '-e', f'MAINFILE={MAINFILE}',
        "-v", f"{comp_in}:/data/in:ro",
        "-v", f"{comp_out}:/data/out",
        comp_image
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
        exec_image
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
        judge_image
    ]


    #building for arm64 and x86_64
    #docker buildx build --platform linux/amd64,linux/arm64 -t d4m14n/stos:cli-1.0.0 .
    
    if build:
        subprocess.run(["docker", "build", "--build-arg", f"LOGS={'on' if logs else 'off'}", "-t", exec_image, exec_path], check=True)
        subprocess.run(["docker", "build", "--build-arg", f"LOGS={'on' if logs else 'off'}", "-t", judge_image, judge_path], check=True)
        subprocess.run(["docker", "build", "-t", comp_image, comp_path], check=True)


    #pushing

    if push:
        platforms = "linux/amd64,linux/arm64"
            # print("Creating a buildx builder with multiarch support...")
            # subprocess.run(["docker", "buildx", "create", "--name", "multiarch-builder", "--use"], check=True)
            # # Initializing the builder and enabling QEMU support
            # print("Initializing the builder...")
            # subprocess.run(["docker", "buildx", "inspect", "--bootstrap"], check=True)
            # # Verifying available builders
            # print("Verifying buildx:")
            # subprocess.run(["docker", "buildx", "ls"], check=True)
    
        subprocess.run(["docker", "login"], check=True)
        subprocess.run([
            "docker", "buildx", "build",
            "--platform", platforms,
            "--build-arg", f"LOGS={'on' if logs else 'off'}",
            "-t", exec_image,
            exec_path,
            "--push"
        ], check=True)

        subprocess.run([
            "docker", "buildx", "build",
            "--platform", platforms,
            "--build-arg", f"LOGS={'on' if logs else 'off'}",
            "-t", judge_image,
            judge_path,
            "--push"
        ], check=True)

        subprocess.run([
            "docker", "buildx", "build",
            "--platform", platforms,
            "-t", comp_image,
            comp_path,
            "--push"
        ], check=True)


    #compiling
    
    if compile:
        start_time = time.time()
        
        try:
            subprocess.run(run_comp_command, check=True)
        except Exception as e:
            print(e)
            return

        print(f">Compilation time: {round(time.time() - start_time, 2)}")



    #executing
    
    start_time = time.time()
    
    try:
        subprocess.run(run_exec_command, check=True)
    except Exception as e:
        print(e)
        return
    
    print(f">Execution time: {round(time.time() - start_time, 2)}")


    #judging

    start_time = time.time()
    
    try:
        subprocess.run(run_judge_command, check=True)
    except Exception as e:
        print(e)
        return

    print(f">Judge time: {round(time.time() - start_time, 2)}")

    #printing resoults
    
    points, result = print_resoults(exec_out)
    print(result)


if __name__ == "__main__":
    #set working directory
    file_dir = os.path.dirname( os.path.abspath(__file__) )
    os.chdir(f"{file_dir}/../..")
    #load .env
    dotenv.load_dotenv(dotenv_path="./src/conf/.env")
    #parse args
    parser = argparse.ArgumentParser(description="Run example")
    parser.add_argument("-b", "--build", action="store_true", default=False, help="Build the docker images")
    parser.add_argument("-l", "--logs", action="store_true", default=False, help="Enable logs")
    parser.add_argument("-p", "--push", action="store_true", default=False, help="Push the docker images")
    parser.add_argument("--no-compile", action="store_false", default=True, help="Disable compiling the code")
    args = parser.parse_args()

    run_example(build=args.build, compile=args.no_compile, logs=args.logs, push=args.push)
