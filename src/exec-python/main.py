import subprocess
import sys
import os
import logging
import time

logger = logging.getLogger("EXEC")


def run_program(test_name: str):
    program_process = subprocess.Popen(
        [
            "python",
            "exec.py",
            "--name", test_name,
            "--time_limit", f"{0}",
            "--total_memory_limit", f"{256 * 1024 * 1024}",
            "--stack_limit", f"{8 * 1024 * 1024}",
        ],
    )
    program_process.wait()


def main():
    os.umask(0)
    start_time = time.time()

    for file in os.listdir(os.getenv("IN")):
        if file.endswith(".in"):
            run_program(file.split(".")[0])

    logger.info(f"exec.py execution time: {round(time.time() - start_time, 2)}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG if os.environ.get("LOGS") == "on" else logging.ERROR,
        format="[%(name)s] %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    main()
