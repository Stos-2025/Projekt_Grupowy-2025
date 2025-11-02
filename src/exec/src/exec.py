import os
import signal
import time
import json
import argparse
import resource
import psutil
import subprocess
from typing import Dict, Tuple, Optional, Any
from common.schemas import ExecOutputSchema


# ===========================
#       ARGUMENT PARSING
# ===========================
def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a sandboxed binary with resource limits.")
    parser.add_argument("--name", "-n", type=str, required=True, help="Name of the test case (without extension).")
    parser.add_argument("--time_limit", "-t", type=float, default=2.0, help="Time limit in seconds.")
    parser.add_argument("--total_memory_limit", "-m", type=int, default=256 * 1024 * 1024, help="Total memory limit in bytes.")
    parser.add_argument("--stack_limit", "-s", type=int, default=0, help="Stack limit in bytes (0 = default 128MB).")
    return parser.parse_args()


# ===========================
#          PATH SETUP
# ===========================
def build_paths(name: str) -> Dict[str, str]:
    """Build and return all necessary file paths."""
    base_paths: Dict[str, str] = {
        "IN": os.getenv("IN", "/data/in"),
        "BIN": os.getenv("BIN", "/data/bin"),
        "STD": os.getenv("STD", "/data/std"),
        "OUT": os.getenv("OUT", "/data/out"),
    }

    return {
        "BINARY": os.path.join(base_paths["BIN"], "program"),
        "INPUT": os.path.join(base_paths["IN"], f"{name}.in"),
        "EXEC": os.path.join(base_paths["OUT"], f"{name}.exec.json"),
        "STDERR": os.path.join(base_paths["STD"], f"{name}.stderr.out"),
        "STDOUT": os.path.join(base_paths["STD"], f"{name}.stdout.out"),
    }


# ===========================
#         PSUTIL HELPERS
# ===========================
def safe_psutil_call(pid: int, func: Any) -> float | int:
    """Safely execute a psutil-based function for a given PID."""
    try:
        process = psutil.Process(pid)
        return func(process)
    except psutil.NoSuchProcess:
        return 0


def get_user_time(pid: int) -> float:
    """Return the user CPU time used by the process."""
    return float(safe_psutil_call(pid, lambda p: p.cpu_times().user)) # type: ignore


def get_memory_usage(pid: int) -> int:
    """Return the resident memory usage (RSS) in bytes."""
    return int(safe_psutil_call(pid, lambda p: p.memory_info().rss)) # type: ignore


# ===========================
#       LIMIT CONFIGURATION
# ===========================
def configure_resource_limits(time_limit: float, memory_limit: int, stack_limit: int) -> None:
    """
    Apply resource limits before running the target binary.
    This function is used as a preexec_fn for subprocess.Popen.
    """
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


# ===========================
#        BINARY EXECUTION
# ===========================
def run_binary(paths: Dict[str, str], time_limit: float, memory_limit: int, stack_limit: int) -> Tuple[int, resource.struct_rusage]:
    """
    Execute the sandboxed binary, monitoring CPU and memory usage.
    Kills the process group if resource limits are exceeded.
    """
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


# ===========================
#        RESULT SAVING
# ===========================
def save_results(exec_path: str, retcode: int, usage: Optional[resource.struct_rusage]) -> None:
    """Save execution metrics to a JSON file."""
    result: ExecOutputSchema = ExecOutputSchema(
        return_code=retcode,
        signal=abs(retcode) if retcode < 0 else None,
        user_time=round(usage.ru_utime, 10) if usage else None,
        total_memory=round(usage.ru_maxrss * 1024, 10) if usage else None,
    )

    with open(exec_path, "w") as file:
        json.dump(result.model_dump(), file, indent=2)


# ===========================
#            MAIN
# ===========================
def main() -> None:
    """Main entry point for the sandbox runner."""
    args: argparse.Namespace = parse_arguments()
    paths = build_paths(args.name)

    try:
        retcode, usage = run_binary(paths, args.time_limit, args.total_memory_limit, args.stack_limit)
        save_results(paths["EXEC"], retcode, usage)
    except Exception:
        save_results(paths["EXEC"], 1, None)


if __name__ == "__main__":
    main()
