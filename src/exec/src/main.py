import json
import os
import sys
import time
import logging
import subprocess
from typing import Optional
from common.schemas import ProblemSpecificationSchema, TestSpecificationSchema


logger = logging.getLogger("EXEC")


def run_test(test_name: str, test: Optional[TestSpecificationSchema] = None):
    if test is None:
        test = TestSpecificationSchema(test_name=test_name)
    program_process = subprocess.Popen(
        [
            "python",
            "exec.py",
            "--name", test_name,
            "--time_limit", f"{test.time_limit}",
            "--total_memory_limit", f"{test.total_memory_limit}",
            "--stack_limit", f"{test.stack_size_limit if test.stack_size_limit else 0}",
        ],
    )
    program_process.wait()


def main():
    os.umask(0)
    start_time = time.time()

    problem_specification: Optional[ProblemSpecificationSchema] = None
    try:
        problem_specification_path = os.path.join(os.environ["CONF"], "problem_specification.json")
        with open(problem_specification_path, 'r') as file:
            problem_specification = ProblemSpecificationSchema.model_validate(json.load(file))
    except Exception:
        problem_specification = None

    #todo change
    if problem_specification:
        for test in problem_specification.tests:
            if test.test_name:
                run_test(test.test_name, test)
    else:
        for file in os.listdir(os.getenv("IN")):
            if file.endswith(".in"):
                test_name = file.split(".")[0]
                run_test(test_name)

    logger.info(f"exec.py execution time: {round(time.time() - start_time, 2)}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG if os.environ.get("LOGS") == "on" else logging.ERROR,
        format="[%(name)s] %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    main()
