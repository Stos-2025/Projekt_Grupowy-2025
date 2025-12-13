#!/usr/bin/env python3

import subprocess
import os
import sys
import time
import dotenv
import argparse
from natsort import natsorted
from typing import List, Optional

file_dir = os.path.dirname( os.path.abspath(__file__) )
os.chdir(f"{file_dir}/..")
sys.path.append(f"{file_dir}/../src/")
from common.schemas import ExecOutputSchema, JudgeOutputSchema, SubmissionResultSchema, TestResultSchema



def get_results(path: str) -> SubmissionResultSchema:
    def fetch_compilation_info(path: str) -> Optional[str]:
        maximum_content_length = 2*5000
        comp_file_path = os.path.join(path, "comp.txt")
        try:
            with open(comp_file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = ""
                for line in f:
                    if len(content) + len(line) > maximum_content_length:
                        break
                    content += line
            
        except Exception:
            return None
        return content if content else None


    result = SubmissionResultSchema()
    points = 0
    test_names: List[str] = []
    for file in os.listdir(path):
        if file.endswith(".judge.json"):
            test_names.append(file.split(".")[0])

    test_names = natsorted(test_names) # type: ignore
    for test_name in test_names:
        try:
            exec_file_path = os.path.join(path, f"{test_name}.exec.json")
            judge_file_path = os.path.join(path, f"{test_name}.judge.json")
            test_result: TestResultSchema = TestResultSchema(test_name=test_name)

            with open(exec_file_path, "r") as exec_file:
                exec_output = ExecOutputSchema.model_validate_json(json_data=exec_file.read())
                test_result.ret_code = exec_output.return_code
                test_result.time = exec_output.user_time
                test_result.memory = exec_output.total_memory

            with open(judge_file_path, "r") as judge_file:
                judge_output = JudgeOutputSchema.model_validate_json(json_data=judge_file.read())
                test_result.grade = judge_output.grade
                test_result.info = judge_output.info
                if judge_output.grade:
                    points += 1

            result.test_results.append(test_result)
        except Exception:
            test_result = TestResultSchema(test_name=test_name, grade=False, info="error while running test")
            result.test_results.append(test_result)


    result.points = points
    try:
        result.info = fetch_compilation_info(path)
    except Exception:
        result.info = "Error while running submission."
        print("Error while fetching compilation info.")

    return result


def run_example(build: bool = True, compile: bool=True, push: bool=False) -> None:
    version = "1.1.0"
    # version = "latest"
    exec_image_tag = f"d4m14n/stos_exec:{version}"
    comp_image_tag = f"d4m14n/stos:gpp_comp-{version}"
    # comp_image_tag = f"d4m14n/stos:python3_comp-{version}"
    judge_image_tag = f"d4m14n/stos_judge:{version}"

    # build = False
    exmp_path = r"./example"
    comp_path = r"./src/compilers/cpp/dockerfile"
    # comp_path = r"./src/compilers/python/dockerfile"
    exec_path = r"./src/exec/dockerfile"
    judge_path = r"./src/judge/dockerfile"

    build_path = r"./src"

    exec_in = exmp_path+"/exec-in"
    conf = exmp_path+"/conf"
    out = exmp_path+"/out"
    comp_in = exmp_path+"/comp-in"
    MAINFILE = "main.py"

    run_comp_command = [
        "docker", "run", 
        "--rm",
        "--ulimit", "cpu=30:30",
        "--network", "none",
        "--security-opt", "no-new-privileges",
        "-e",
        "BIN=/data/out",
        '-e', f'MAINFILE={MAINFILE}',
        "-v", f"{comp_in}:/data/in:ro",
        "-v", f"{out}:/data/out",
        comp_image_tag
    ]
    run_exec_command = [
        "docker", "run", 
        "--rm",
        "--ulimit", "cpu=30:30",
        "--network", "none",
        "-e", "LOG=/data/logs/exec.log",
        "--security-opt", "no-new-privileges",
        "-v", f"{conf}:/data/conf:ro",
        "-v", f"{exec_in}:/data/in:ro",
        "-v", f"{out}:/data/bin:ro",
        "-v", f"{out}:/data/out",
        "-v", f"{exmp_path}/logs:/data/logs",
        exec_image_tag
    ]
    run_judge_command = [  
        "docker", "run", 
        "--rm",
        "--ulimit", "cpu=30:30",
        "--network", "none",
        "--security-opt", "no-new-privileges",
        "-v", f"{conf}:/data/conf:ro",
        "-v", f"{out}:/data/in:ro",
        "-v", f"{out}:/data/out",
        "-v", f"{exec_in}:/data/answer:ro",
        judge_image_tag
    ]


    
    if build:
        subprocess.run(["docker", "build", "-t", exec_image_tag, "-f", exec_path, build_path], check=True)
        subprocess.run(["docker", "build", "-t", judge_image_tag, "-f", judge_path, build_path], check=True)
        subprocess.run(["docker", "build", "-t", comp_image_tag, "-f", comp_path, build_path], check=True)



    if push:
        subprocess.run(["docker", "login"], check=True)

        subprocess.run(["docker", "push", exec_image_tag], check=True)
        subprocess.run(["docker", "push", judge_image_tag], check=True)
        # subprocess.run(["docker", "push", comp_image_tag], check=True)



    if compile:
        start_time = time.time()
        
        try:
            subprocess.run(run_comp_command, check=True)
        except Exception as e:
            print(e)
            return

        print(f">Compilation time: {round(time.time() - start_time, 2)}")



    
    start_time = time.time()
    
    try:
        subprocess.run(run_exec_command, check=True)
    except Exception as e:
        print(e)
        return
    
    print(f">Execution time: {round(time.time() - start_time, 2)}")



    start_time = time.time()
    
    try:
        subprocess.run(run_judge_command, check=True)
    except Exception as e:
        print(e)
        return

    print(f">Judge time: {round(time.time() - start_time, 2)}")


    result = get_results(out)
    print(result)



if __name__ == "__main__":
    #set working directory
   
    # load .env
    dotenv.load_dotenv(dotenv_path="./src/conf/.env")
    #parse args
    parser = argparse.ArgumentParser(description="Run example")
    parser.add_argument("-b", "--build", action="store_true", default=False, help="Build the docker images")
    parser.add_argument("-p", "--push", action="store_true", default=False, help="Push the docker images")
    parser.add_argument("--no-compile", action="store_false", default=True, help="Disable compiling the code")
    args = parser.parse_args()

    run_example(build=args.build, compile=args.no_compile, push=args.push)
