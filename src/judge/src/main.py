import os
import json
from judge import check # type: ignore
from common.schemas import ProblemSpecificationSchema, TestSpecificationSchema


def get_default_problem_specification() -> ProblemSpecificationSchema:
    problem_specification = ProblemSpecificationSchema(id="default_problem")
    for file in os.listdir(os.getenv("ANS", "/data/answer")):
        if file.endswith(".out"):
            test_name = file.split(".")[0]
            test_spec = TestSpecificationSchema(test_name=test_name)
            problem_specification.tests.append(test_spec)
    return problem_specification


def main():
    problem_specification: ProblemSpecificationSchema
    try:
        problem_specification_path = os.path.join(os.getenv("CONF", "/data/conf"), "problem_specification.json")
        with open(problem_specification_path, 'r') as file:
            problem_specification = ProblemSpecificationSchema.model_validate(json.load(file))
    except Exception:
        problem_specification = get_default_problem_specification()

    

    os.umask(0)
    for test in problem_specification.tests:
        check(test.test_name, test.time_limit, test.total_memory_limit)
    
   
if __name__ == "__main__":
    main()