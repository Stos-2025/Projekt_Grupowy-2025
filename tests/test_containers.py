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