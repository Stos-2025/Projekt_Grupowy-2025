import os
import json
import judge 
from common.schemas import JudgeOutputSchema, ProblemSpecificationSchema, TestSpecificationSchema


# def get_default_problem_specification() -> ProblemSpecificationSchema:
#     problem_specification = ProblemSpecificationSchema(id="default_problem")
#     for file in os.listdir(os.getenv("ANS", "/data/answer")):
#         if file.endswith(".out"):
#             test_name = file.split(".")[0]
#             test_spec = TestSpecificationSchema(test_id=test_name)
#             problem_specification.tests.append(test_spec)
#     return problem_specification


def main():
    problem_specification: ProblemSpecificationSchema
    try:
        problem_specification_path = os.path.join(os.getenv("CONF", "/data/conf"), "problem_specification.json")
        with open(problem_specification_path, 'r') as file:
            problem_specification = ProblemSpecificationSchema.model_validate(json.load(file))
    except Exception:
        raise
        # problem_specification = get_default_problem_specification()

    

    os.umask(0)
    for test in problem_specification.tests:
        output_file = test.output_file or f"{test.test_id}.out"
        test_result = judge.judge_test(test.test_id, output_file, test.time_limit, test.total_memory_limit)
        output = JudgeOutputSchema()
        if test_result is None:
            continue
        output.grade = test_result.grade
        output.info = test_result.info
        with open(f"{os.getenv('OUT')}/{test.test_id}.judge.json", "w") as judge_file:
            json.dump(output.model_dump(), judge_file, indent=2)
   
    
   
if __name__ == "__main__":
    main()