import json
import os
import signal
from typing import NamedTuple
from common.schemas import ExecOutputSchema, JudgeOutputSchema

class TestResult(NamedTuple):
    grade: bool = False
    info: str = ""


def check_comp(comp_path: str) -> TestResult:
    try:
        with open(comp_path, "r") as comp_file:
            comp = json.load(comp_file)
            if comp["return_code"] != 0:
                return TestResult(False, f"compilation failed with return code {comp['return_code']}")
    except Exception:
        pass
    return TestResult(True, "ok c")


def check_exec(exec_path: str, time_limit: float, memory_limit: int) -> TestResult:
    # Validate file existence
    try:
        with open(exec_path, "r") as exec_file:
            exec_output = ExecOutputSchema.model_validate_json(exec_file.read().strip())
    except Exception as e:
        return TestResult(False, f"execution failed: {e}")
    rc: int = exec_output.return_code

    # Time/memory limit exceeded (SIGKILL)
    if exec_output.user_time is not None and exec_output.user_time >= time_limit:
        return TestResult(False, "time limit exceeded")
    
    if exec_output.total_memory is not None and exec_output.total_memory >= memory_limit:
        return TestResult(False, "memory limit exceeded")

    # if rc == -9:
        # return TestResult(False, "process killed (unknown reason)")

    # Segmentation fault
    if rc == -11:
        return TestResult(False, "segmentation fault")

    # Positive return code → program error
    if rc > 0:
        return TestResult(False, f"program exited with {rc}")

    # Negative code (other signals than -9/-11)
    if rc < 0:
        return TestResult(False, signal.Signals(-rc).name.lower())

    # OK — test passed
    return TestResult(True, "ok")



def judge(answer_path: str, input_path: str) -> TestResult:
    # check files exist and are readable and answer is not too big
    if not os.path.exists(answer_path) or not os.path.exists(input_path):
        return TestResult(False, "")
    if os.path.getsize(answer_path) > 5 * 1024 * 1024:  # 5 GiB limit
        return TestResult(False, "answer file is too big")


    info = "ok"
    line_nr = 0
    with open(answer_path, "r") as answer, open(input_path, "r") as input:
        for line in answer:
            line_nr += 1
            try:
                output_line = input.readline()
            except EOFError:
                info = f"unexpected EOF in line {line_nr}"
                return TestResult(False, info)
            if line.strip() != output_line.strip():
                info = f"line {line_nr} is not correct"
                return TestResult(False, info)
    return TestResult(True, info)



def check(name: str, time_limit: float, memory_limit: int) -> None:          
    answer_path = os.path.join(os.getenv('ANS', '/data/answer'), f"{name}.out")
    input_path = os.path.join(os.getenv('IN', '/data/in'), f"{name}.stdout.out")
    comp_path = os.path.join(os.getenv('OUT', '/data/out'), "comp.json")
    exec_path = os.path.join(os.getenv('OUT', '/data/out'), f"{name}.exec.json")

    output = JudgeOutputSchema()
    res = check_comp(comp_path)
    if not res.grade:
        return
    if res.grade:
        res = check_exec(exec_path, time_limit, memory_limit)
    if res.grade:
        res = judge(answer_path, input_path)

    output.grade = res.grade
    output.info = res.info
    with open(f"{os.getenv('OUT')}/{name}.judge.json", "w") as judge_file:
        json.dump(output.model_dump(), judge_file, indent=2)
        