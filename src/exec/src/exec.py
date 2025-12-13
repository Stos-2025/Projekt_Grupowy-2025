import os
import signal
import time
import json
import argparse
import resource
import psutil
import subprocess
import envs
from logger import logger 
from typing import Dict, Tuple, Optional, Any
from common.schemas import ExecOutputSchema


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a sandboxed binary with resource limits.")
    parser.add_argument("--name", "-n", type=str, required=True, help="Name of the test case (without extension).")
    parser.add_argument("--time_limit", "-t", type=float, default=2.0, help="Time limit in seconds.")
    parser.add_argument("--total_memory_limit", "-m", type=int, default=256 * 1024 * 1024, help="Total memory limit in bytes.")
    parser.add_argument("--stack_limit", "-s", type=int, default=0, help="Stack limit in bytes (0 = default 128MB).")
    parser.add_argument("--input_file", "-i", type=str, help="Path to the input file.")
    parser.add_argument("--output_file", "-o", type=str, help="Path to the output file.")
    return parser.parse_args()


def build_paths(name: str, input_file: str, output_file: str) -> Dict[str, str]:
    base_paths: Dict[str, str] = {
        "IN": envs.IN,
        "BIN": envs.BIN,
        "STD": envs.STD,
        "OUT": envs.OUT,
    }

    return {
        "BINARY": os.path.join(base_paths["BIN"], "program"),
        "INPUT": os.path.join(base_paths["IN"], input_file),
        "ANSWER": os.path.join(base_paths["IN"], output_file),
        "RESULT": os.path.join(base_paths["OUT"], f"{name}.exec.json"),
        "STDERR": os.path.join(base_paths["STD"], f"{name}.stderr.out"),
        "STDOUT": os.path.join(base_paths["STD"], f"{name}.stdout.out"),
    }


def safe_psutil_call(pid: int, func: Any) -> float | int:
    try:
        process = psutil.Process(pid)
        return func(process)
    except psutil.NoSuchProcess:
        return 0


def get_user_time(pid: int) -> float:
    return float(safe_psutil_call(pid, lambda p: p.cpu_times().user)) # type: ignore


def get_memory_usage(pid: int) -> int:
    return int(safe_psutil_call(pid, lambda p: p.memory_info().rss)) # type: ignore


def configure_resource_limits(time_limit: float, memory_limit: int, stack_limit: int) -> None:
    time_limit_sec = int(time_limit) + 1
    memory_limit_bytes = memory_limit * 2  # Overcommit safety margin
    stack_limit_bytes = stack_limit if stack_limit > 0 else 256 * 1024 * 1024  # 256 MB default
    print(f"Configuring resource limits: time={time_limit_sec}s, memory={memory_limit_bytes}B, stack={stack_limit_bytes}B")

    limits = {
        resource.RLIMIT_CPU: (time_limit_sec, time_limit_sec),
        resource.RLIMIT_AS: (memory_limit_bytes, memory_limit_bytes),
        resource.RLIMIT_STACK: (stack_limit_bytes, stack_limit_bytes),
        resource.RLIMIT_CORE: (0, 0),  # Disable core dumps
    }

    for limit, values in limits.items():
        resource.setrlimit(limit, values)

    # Create a new process group so that SIGKILL can target the entire group.
    os.setsid()


def run_binary(
        paths: Dict[str, str], 
        time_limit: float, 
        memory_limit: int, 
        stack_limit: int
    ) -> Tuple[int, resource.struct_rusage]:
    binary_path = paths["BINARY"]
    input_path = paths["INPUT"]

    if not os.path.isfile(binary_path) or not os.access(binary_path, os.X_OK):
        raise FileNotFoundError(f"Binary not found or not executable: {binary_path}")
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file missing: {input_path}")

    with open(input_path, "r") as fin, open(paths["STDERR"], "w") as ferr, open(paths["STDOUT"], "w") as fout:
        process = subprocess.Popen(
            [binary_path],
            stdin=fin,
            stderr=ferr,
            stdout=fout,
            preexec_fn=lambda: configure_resource_limits(time_limit, memory_limit, stack_limit),
        )

        check_interval = 0.01

        while process.poll() is None:
            user_time = get_user_time(process.pid)
            memory_used = get_memory_usage(process.pid)

            if user_time >= time_limit - check_interval:
                check_interval = 0.001  # Increase precision near time limit

            if user_time > time_limit or memory_used > memory_limit:
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                process.wait()
                break

            time.sleep(check_interval)

    usage: resource.struct_rusage = resource.getrusage(resource.RUSAGE_CHILDREN)
    return process.returncode, usage


def save_results(exec_path: str, retcode: int, usage: Optional[resource.struct_rusage]) -> None:
    result: ExecOutputSchema = ExecOutputSchema(
        return_code=retcode,
        signal=abs(retcode) if retcode < 0 else None,
        user_time=round(usage.ru_utime, 10) if usage else None,
        total_memory=round(usage.ru_maxrss * 1024, 10) if usage else None,
    )

    with open(exec_path, "w") as file:
        json.dump(result.model_dump(), file, indent=2)


def main() -> None:
    args: argparse.Namespace = parse_arguments()
    paths = build_paths(args.name, args.input_file, args.output_file)

    logger.info(f"Running test '{args.name}' with time limit {args.time_limit}s, memory limit {args.total_memory_limit}B, stack limit {args.stack_limit}B")
    try:
        retcode, usage = run_binary(paths, args.time_limit, args.total_memory_limit, args.stack_limit)
        
        logger.info(f"Test '{args.name}' finished with return code {retcode}, user time {usage.ru_utime if usage else 'N/A'}, total memory {usage.ru_maxrss * 1024 if usage else 'N/A'}")

        save_results(paths["RESULT"], retcode, usage)
    except Exception as e:
        logger.exception(f"An error occurred while running test '{args.name}': {e}")
        save_results(paths["RESULT"], 1, None)


if __name__ == "__main__":
    main()
