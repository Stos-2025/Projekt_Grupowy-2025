import os
import shutil
import json
import subprocess
import pytest

CPP_COMPILER_IMAGE = "comp"
COMPILER_ENTRYPOINT = [
    "docker", "run", "--rm",
    "-e", "BIN=/data/out",
    "-v", None,  # input
    "-v", None,  # output
    CPP_COMPILER_IMAGE
]

EXAMPLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/example/comp-in"))

@pytest.fixture
def cpp_example_files():
    files = ["main.cpp", "add.cpp", "add.h"]
    return files


def run_cpp_compiler(input_dir, output_dir):
    cmd = COMPILER_ENTRYPOINT.copy()
    cmd[6] = f"{input_dir}:/data/in:ro"
    cmd[8] = f"{output_dir}:/data/out"
    subprocess.run(cmd, check=False)


def test_cpp_compiler_success(tmp_path, cpp_example_files):
    # Przygotuj wejście
    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    in_dir.mkdir()
    out_dir.mkdir()
    for fname in cpp_example_files:
        shutil.copy(os.path.join(EXAMPLE_DIR, fname), in_dir / fname)
    # Uruchom kompilator
    run_cpp_compiler(str(in_dir), str(out_dir))
    # Sprawdź plik comp.json
    comp_json = out_dir / "comp.json"
    assert comp_json.exists(), "Brak pliku comp.json"
    with open(comp_json) as f:
        meta = json.load(f)
    assert meta["return_code"] == 0, f"Kompilacja nie powiodła się: {meta}"
    # Sprawdź plik binarny
    # (w /tmp/bin, ale kopiowany do BIN=/data/out)
    assert any("program" in f.name for f in out_dir.iterdir()), "Brak pliku binarnego program"


def test_cpp_compiler_error(tmp_path, cpp_example_files):
    # Przygotuj wejście z błędem
    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    in_dir.mkdir()
    out_dir.mkdir()
    for fname in cpp_example_files:
        shutil.copy(os.path.join(EXAMPLE_DIR, fname), in_dir / fname)
    # Popsuj main.cpp
    with open(in_dir / "main.cpp", "a") as f:
        f.write("\nthis_is_not_valid_cpp_code\n")
    # Uruchom kompilator
    run_cpp_compiler(str(in_dir), str(out_dir))
    # Sprawdź plik comp.json
    comp_json = out_dir / "comp.json"
    assert comp_json.exists(), "Brak pliku comp.json"
    with open(comp_json) as f:
        meta = json.load(f)
    assert meta["return_code"] != 0, "Kompilacja powinna się nie powieść"
    # Plik binarny nie powinien powstać
    assert not any("program" in f.name for f in out_dir.iterdir()), "Plik binarny nie powinien powstać"


def test_cpp_compiler_no_sources(tmp_path):
    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    in_dir.mkdir()
    out_dir.mkdir()
    # Uruchom kompilator na pustym katalogu
    run_cpp_compiler(str(in_dir), str(out_dir))
    comp_json = out_dir / "comp.json"
    assert comp_json.exists(), "Brak pliku comp.json"
    with open(comp_json) as f:
        meta = json.load(f)
    assert meta["return_code"] != 0, "Kompilacja powinna się nie powieść na pustym katalogu"


def run_pipeline(comp_in, comp_out, exec_in, exec_out, answer_out, build=False):
    """Uruchamia pipeline dockerowy na podanych katalogach."""
    # Kompilacja
    comp_cmd = [
        "docker", "run", "--rm",
        "--ulimit", "cpu=30:30",
        "--network", "none",
        "--security-opt", "no-new-privileges",
        "-e", "BIN=/data/out",
        "-v", f"{comp_in}:/data/in:ro",
        "-v", f"{comp_out}:/data/out",
        "comp"
    ]
    exec_cmd = [
        "docker", "run", "--rm",
        "--ulimit", "cpu=30:30",
        "--network", "none",
        "--security-opt", "no-new-privileges",
        "-e", "LOGS=on",
        "-v", f"{exec_in}/in:/data/in:ro",
        "-v", f"{comp_out}:/data/bin:ro",
        "-v", f"{exec_out}:/data/out",
        "exec"
    ]
    judge_cmd = [
        "docker", "run", "--rm",
        "--ulimit", "cpu=30:30",
        "--network", "none",
        "--security-opt", "no-new-privileges",
        "-e", "LOGS=on",
        "-v", f"{exec_out}:/data/in:ro",
        "-v", f"{exec_out}:/data/out",
        "-v", f"{exec_in}/out:/data/answer:ro",
        "judge"
    ]
    subprocess.run(comp_cmd, check=False)
    subprocess.run(exec_cmd, check=False)
    subprocess.run(judge_cmd, check=False)


def test_cpp_pipeline_infinite_loop(tmp_path):
    comp_in = tmp_path / "comp-in"
    comp_out = tmp_path / "comp-out"
    exec_in = tmp_path / "exec-in"
    exec_out = tmp_path / "exec-out"
    for d in [comp_in, comp_out, exec_in, exec_out]:
        d.mkdir()
    (exec_in / "in").mkdir()
    (exec_in / "out").mkdir()
    #nieskończona pętla
    code = """
    int main() {
        while(1) {}
        return 0;
    }
    """
    with open(comp_in / "main.cpp", "w") as f:
        f.write(code)
    # Dane wejściowe i oczekiwane wyjście
    with open(exec_in / "in" / "0.in", "w") as f:
        f.write("1\n")
    with open(exec_in / "out" / "0.out", "w") as f:
        f.write("1\n")
    run_pipeline(str(comp_in), str(comp_out), str(exec_in), str(exec_out), str(exec_in / "out"))
    # Sprawdź wynik wykonania
    exec_json = exec_out / "0.exec.json"
    assert exec_json.exists(), "Brak pliku exec.json (timeout?)"
    with open(exec_json) as f:
        meta = json.load(f)
    # Oczekujemy return_code != 0 (timeout/kill)
    assert meta["return_code"] != 0, f"Program nie został przerwany: {meta}"


def test_cpp_pipeline_system_access(tmp_path):
    comp_in = tmp_path / "comp-in"
    comp_out = tmp_path / "comp-out"
    exec_in = tmp_path / "exec-in"
    exec_out = tmp_path / "exec-out"
    for d in [comp_in, comp_out, exec_in, exec_out]:
        d.mkdir()
    (exec_in / "in").mkdir()
    (exec_in / "out").mkdir()
    # próba zapisu do /etc/passwd
    code = """
    #include <fstream>\nint main() { std::ofstream f(\"/etc/passwd\"); f << \"hacked\"; return 0; }\n"""
    with open(comp_in / "main.cpp", "w") as f:
        f.write(code)
    # Dane wejściowe i oczekiwane wyjście
    with open(exec_in / "in" / "0.in", "w") as f:
        f.write("1\n")
    with open(exec_in / "out" / "0.out", "w") as f:
        f.write("1\n")

    run_pipeline(str(comp_in), str(comp_out), str(exec_in), str(exec_out), str(exec_in / "out"))
    # sprawdzam stderr
    stderr_file = exec_out / "0.stderr.out"
    assert stderr_file.exists(), "Brak pliku stderr.out (sandbox?)"
    with open(stderr_file) as f:
        stderr_content = f.read()
    assert ("Permission denied" in stderr_content or "permission denied" in stderr_content or "Operation not permitted" in stderr_content or "operation not permitted" in stderr_content), f"Brak komunikatu o odmowie dostępu: {stderr_content}"

def test_cpp_pipeline_system_access_var_log(tmp_path):
    comp_in = tmp_path / "comp-in"
    comp_out = tmp_path / "comp-out"
    exec_in = tmp_path / "exec-in"
    exec_out = tmp_path / "exec-out"
    for d in [comp_in, comp_out, exec_in, exec_out]:
        d.mkdir()
    (exec_in / "in").mkdir()
    (exec_in / "out").mkdir()
    # Próba zapisu do /var/log/hacked.log
    code = """
    #include <fstream>\nint main() { std::ofstream f(\"/var/log/hacked.log\"); f << \"hacked\"; return 0; }\n"""
    with open(comp_in / "main.cpp", "w") as f:
        f.write(code)
    with open(exec_in / "in" / "0.in", "w") as f:
        f.write("1\n")
    with open(exec_in / "out" / "0.out", "w") as f:
        f.write("1\n")
    run_pipeline(str(comp_in), str(comp_out), str(exec_in), str(exec_out), str(exec_in / "out"))
    stderr_file = exec_out / "0.stderr.out"
    assert stderr_file.exists(), "Brak pliku stderr.out (/var/log)"
    with open(stderr_file) as f:
        stderr_content = f.read()
    assert ("Permission denied" in stderr_content or "permission denied" in stderr_content or "Operation not permitted" in stderr_content or "operation not permitted" in stderr_content), f"Brak komunikatu o odmowie dostępu: {stderr_content}"
