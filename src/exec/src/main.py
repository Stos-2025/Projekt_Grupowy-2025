import json
import os
import subprocess
from logger import logger
from typing import List
from common.schemas import ProblemSpecificationSchema, TestSpecificationSchema




def run_test(test: TestSpecificationSchema) -> None:
    def build_test_args(test: TestSpecificationSchema) -> List[str]:
        return [
            "python",
            "exec.py",
            "--name", test.test_id,
            "--input_file", f"{test.input_file or f'{test.test_id}.in'}",
            "--output_file", f"{test.output_file or f'{test.test_id}.out'}",
            "--time_limit", str(test.time_limit),
            "--total_memory_limit", str(test.total_memory_limit),
            "--stack_limit", str(test.stack_size_limit or 0),
        ]
    
    args = build_test_args(test)
    subprocess.run(args, check=True)  # raise exception jeśli proces zakończy się błędem


# def get_default_problem_specification() -> ProblemSpecificationSchema:
#     in_dir = os.getenv("IN", "/data/in")
#     problem_spec = ProblemSpecificationSchema(id="default_problem")

#     for file in os.listdir(in_dir):
#         if file.endswith(".in"):
#             test_name = os.path.splitext(file)[0]
#             problem_spec.tests.append(TestSpecificationSchema(test_id=test_name))

#     return problem_spec




def main() -> None:
    logger.info("Starting test execution environment setup.")
    conf_dir = os.getenv("CONF", "/data/conf")
    problem_spec_path = os.path.join(conf_dir, "problem_specification.json")

    with open(problem_spec_path, 'r') as f:
        problem_spec = ProblemSpecificationSchema.model_validate(json.load(f))

    logger.info(f"Loaded problem specification for problem ID: {problem_spec.id}")

    for test in problem_spec.tests:
        try:
            logger.info(f"Running test: {test.test_id}")
            run_test(test)
            logger.info(f"Test {test.test_id} completed successfully.")
        except Exception as e:
            logger.error(f"Error running test {test.test_id}: {e}")
    logger.info("All tests executed.")

if __name__ == "__main__":
    main()
