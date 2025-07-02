import os
import time
import json
import argparse
import resource
import subprocess
from typing import Tuple, Optional

import psutil

parser = argparse.ArgumentParser()
parser.add_argument("--name", "-n", type=str, required=True, help="Name of the test case (without extension)")
parser.add_argument("--time_limit", "-t", type=float, default=2, help="Time limit in seconds")
parser.add_argument("--total_memory_limit", "-m", type=int, default=256 * 1024 * 1024, help="Total memory limit in bytes")
parser.add_argument("--stack_limit", "-s", type=int, default=0, help="Stack limit in bytes")
args = parser.parse_args()

name: str = args.name
stack_limit: int = args.stack_limit
time_limit: float = args.time_limit
memory_limit: int = args.total_memory_limit

IN = os.environ["IN"]
BIN = os.environ["BIN"]
STD = os.environ["STD"]
OUT = os.environ["OUT"]

BINARY_PATH = os.path.join(BIN, "program")
INPUT_PATH = os.path.join(IN, f"{name}.in")
EXEC_PATH = os.path.join(OUT, f"{name}.exec.json")
ERROR_PATH = os.path.join(STD, f"{name}.stderr.out")
OUTPUT_PATH = os.path.join(STD, f"{name}.stdout.out")


def set_limits():
    # CPU time limit (RLIMIT_CPU)
    resource.setrlimit(resource.RLIMIT_CPU, (int(time_limit) + 1, int(time_limit) + 1))
    # Virtual memory limit (RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
    # Stack size limit (RLIMIT_STACK)
    if stack_limit > 0:
        resource.setrlimit(resource.RLIMIT_STACK, (stack_limit, stack_limit))

    # Output file size limit (RLIMIT_FSIZE)
    # resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
    # Block creation of core dumps
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def get_process_user_time(pid: int) -> float:
    """Pobiera user time dla działającego procesu używając psutil"""
    try:
        process = psutil.Process(pid)
        cpu_times = process.cpu_times()
        return cpu_times.user
    except psutil.NoSuchProcess:
        return 0
    

def run_binary() -> Tuple[int, resource.struct_rusage]:
    # Check if the binary and input files exist
    if not os.path.isfile(BINARY_PATH) or not os.access(BINARY_PATH, os.X_OK):
        raise FileNotFoundError("Binary file does not exist or is not executable")
    if not os.path.isfile(INPUT_PATH):
        raise FileNotFoundError("Input file does not exist")

    # running the program
    with open(INPUT_PATH, "r") as input_file, open(ERROR_PATH, "w") as error_file, open(
        OUTPUT_PATH, "w"
    ) as output_file:
        program_process = subprocess.Popen(
            [BINARY_PATH],
            stdin=input_file,
            stderr=error_file,
            stdout=output_file,
            preexec_fn=set_limits,
        )
        
        check_interval = 0.01 
        while program_process.poll() is None:
            try:
                current_user_time = get_process_user_time(program_process.pid)
                if current_user_time >= time_limit-check_interval:
                    check_interval = 0.001
                if current_user_time > time_limit:
                    program_process.kill()
                    program_process.wait()
                    break
            except Exception:
                continue
            time.sleep(check_interval)

    # reading resource usage
    return program_process.returncode, resource.getrusage(resource.RUSAGE_CHILDREN)


def save_program_results(
    retcode: int, metrics: Optional[resource.struct_rusage]
) -> None:
    meta = {}
    meta["return_code"] = retcode
    meta["signal"] = abs(retcode) if retcode < 0 else None
    if metrics is not None:
        meta["user_time"] = round(metrics.ru_utime, 10)
        meta["memory"] = round(metrics.ru_maxrss, 10)
        # ...

    with open(EXEC_PATH, "w") as exec_file:
        json.dump(meta, exec_file)


if __name__ == "__main__":
    try:
        code, metrics = run_binary()
        save_program_results(code, metrics)
    except Exception as e:
        save_program_results(2, None)
