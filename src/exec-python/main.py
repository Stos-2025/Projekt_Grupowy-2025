import json
import os
import sys
import time
import logging
import subprocess
from pydantic import BaseModel
from typing import List, Optional


logger = logging.getLogger("EXEC")
class TestSpecification(BaseModel):
    test_name: str = ""
    time_limit: float = 2
    total_memory_limit: int = 256*1024*1024  # 256 MB
    stack_size_limit: Optional[int] = None
class ProblemSpecification(BaseModel):
    id: Optional[str]
    tests: List[TestSpecification] = []

def run_test(test_name: str, test: Optional[TestSpecification] = None):
    if test is None:
        test = TestSpecification(test_name=test_name)
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

    problem_specification: Optional[ProblemSpecification] = None
    try:
        problem_specification_path = os.path.join(os.environ["CONF"], "problem_specification.json")
        with open(problem_specification_path, 'r') as file:
            problem_specification = ProblemSpecification.model_validate(json.load(file))
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
