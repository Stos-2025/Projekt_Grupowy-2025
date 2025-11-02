import json
import os
import subprocess
from typing import List
from common.schemas import ProblemSpecificationSchema, TestSpecificationSchema


def build_test_args(test: TestSpecificationSchema) -> List[str]:
    """Zbuduj listę argumentów do uruchomienia exec.py dla pojedynczego testu."""
    return [
        "python",
        "exec.py",
        "--name", test.test_name,
        "--time_limit", str(test.time_limit),
        "--total_memory_limit", str(test.total_memory_limit),
        "--stack_limit", str(test.stack_size_limit or 0),
    ]


def run_test(test: TestSpecificationSchema) -> None:
    """Uruchom pojedynczy test."""
    args = build_test_args(test)
    subprocess.run(args, check=True)  # raise exception jeśli proces zakończy się błędem


def get_default_problem_specification() -> ProblemSpecificationSchema:
    """Wygeneruj domyślną specyfikację problemu na podstawie plików .in w katalogu IN."""
    in_dir = os.getenv("IN", "/data/in")
    problem_spec = ProblemSpecificationSchema(id="default_problem")

    for file in os.listdir(in_dir):
        if file.endswith(".in"):
            test_name = os.path.splitext(file)[0]
            problem_spec.tests.append(TestSpecificationSchema(test_name=test_name))

    return problem_spec


def load_problem_specification() -> ProblemSpecificationSchema:
    """Wczytaj specyfikację problemu z pliku JSON lub zwróć domyślną."""
    conf_dir = os.getenv("CONF", "/data/conf")
    problem_spec_path = os.path.join(conf_dir, "problem_specification.json")

    try:
        with open(problem_spec_path, 'r') as f:
            return ProblemSpecificationSchema.model_validate(json.load(f))
    except Exception:
        return get_default_problem_specification()


def main() -> None:
    os.umask(0)  # ustawienie domyślnego maskowania plików
    problem_spec = load_problem_specification()
    print("Loaded problem specification:\n", problem_spec)

    for test in problem_spec.tests:
        run_test(test)


if __name__ == "__main__":
    main()
