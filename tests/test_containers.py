import os
import subprocess
import json
import pytest

@pytest.fixture
def setup_environment():
    # Prepare directories for testing
    base_path = "./src/example"
    paths = {
        "comp_in": f"{base_path}/comp-in",
        "comp_out": f"{base_path}/comp-out",
        "exec_in": f"{base_path}/exec-in",
        "exec_out": f"{base_path}/exec-out",
    }
    for path in paths.values():
        os.makedirs(path, exist_ok=True)
    yield paths
    # Cleanup after tests
    for path in paths.values():
        subprocess.run(["rm", "-rf", path])

def test_compilation_container(setup_environment):
    paths = setup_environment
    comp_command = [
        "docker", "run",
        "--rm",
        "-v", f"{paths['comp_in']}:/data/in:ro",
        "-v", f"{paths['comp_out']}:/data/out",
        "comp"
    ]
    # Add a sample C++ file for testing
    cpp_code = """
    #include <iostream>
    int main() {
        std::cout << "Hello, World!" << std::endl;
        return 0;
    }
    """
    with open(f"{paths['comp_in']}/main.cpp", "w") as f:
        f.write(cpp_code)
    result = subprocess.run(comp_command, capture_output=True)
    assert result.returncode == 0, f"Compilation failed: {result.stderr.decode()}"
    assert os.path.exists(f"{paths['comp_out']}/program"), "Compiled binary not found"

def test_execution_container(setup_environment):
    paths = setup_environment
    exec_command = [
        "docker", "run",
        "--rm",
        "-e", "LOGS=on",
        "-v", f"{paths['exec_in']}/in:/data/in:ro",
        "-v", f"{paths['comp_out']}:/data/bin:ro",
        "-v", f"{paths['exec_out']}:/data/out",
        "exec"
    ]
    # Add input data for testing
    os.makedirs(f"{paths['exec_in']}/in", exist_ok=True)
    with open(f"{paths['exec_in']}/in/0.in", "w") as f:
        f.write("1\n")
    result = subprocess.run(exec_command, capture_output=True)
    assert result.returncode == 0, f"Execution failed: {result.stderr.decode()}"
    assert os.path.exists(f"{paths['exec_out']}/0.stdout.out"), "Execution output not found"

def test_judge_container(setup_environment):
    paths = setup_environment
    judge_command = [
        "docker", "run",
        "--rm",
        "-e", "LOGS=on",
        "-v", f"{paths['exec_out']}:/data/in:ro",
        "-v", f"{paths['exec_out']}:/data/out",
        "-v", f"{paths['exec_in']}/out:/data/answer:ro",
        "judge"
    ]
    # Add expected output for testing
    os.makedirs(f"{paths['exec_in']}/out", exist_ok=True)
    with open(f"{paths['exec_in']}/out/0.out", "w") as f:
        f.write("Hello, World!\n")
    result = subprocess.run(judge_command, capture_output=True)
    assert result.returncode == 0, f"Judging failed: {result.stderr.decode()}"
    assert os.path.exists(f"{paths['exec_out']}/0.judge.json"), "Judge output not found"
    with open(f"{paths['exec_out']}/0.judge.json", "r") as f:
        judge_result = json.load(f)
    assert judge_result["grade"] == 1, "Judging failed: Incorrect grade"
