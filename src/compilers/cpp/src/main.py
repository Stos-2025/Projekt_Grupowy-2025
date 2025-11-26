#!/usr/bin/env python3

import subprocess
import json
import os
import shutil
import sys

SRC: str = os.environ["SRC"]
OUT: str = os.environ["OUT"]
BIN: str = os.environ["BIN"]

SRC_TMP: str = "/src"
BIN_TMP: str = "/program"
OUT_TMP: str = "/out"
DIAGNOSTIC_FILE: str = f"{OUT}/comp.txt"
STYLE_FILE: str = f"{OUT}/comp.txt"
OUT_FILE: str = f"{OUT}/comp.json"

def copy_src_files():
    os.makedirs(SRC_TMP, exist_ok=True)
    if not os.listdir(SRC):
        raise FileNotFoundError(f"No source provided")
    for file_name in os.listdir(SRC):
        full_file_name = os.path.join(SRC, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, SRC_TMP)


def compile():
    cmd = [
        "g++",
        "-Wall", "-Wextra", "-Wpedantic",
        "-fdiagnostics-color=always",
        "-std=c++17",
        "-o", f"{BIN_TMP}/program"
    ] + [f"{SRC_TMP}/*.cpp"]

    with open(DIAGNOSTIC_FILE, "w", encoding="utf-8") as diag_file:
        result = subprocess.run(
            " ".join(cmd),
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=diag_file
        )
    write_meta(result.returncode)


def write_meta(return_code: int) -> None:
    """Write the OUT_FILE metadata with the given return code.

    This helper is used when an error occurs before `compile()` can
    produce the output JSON, so callers can still produce a consistent
    `out.json` file with a non-zero return code.
    """
    meta = {"return_code": int(return_code)}
    try:
        # Ensure output directory exists (in case of earlier failures)
        os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
        with open(OUT_FILE, "w", encoding="utf-8") as out_file:
            json.dump(meta, out_file)
    except Exception as e:
        # If we cannot write the meta file, print to stderr but do not raise.
        print(f"Failed to write meta to {OUT_FILE}: {e}", file=sys.stderr)
    
def copy_out_files():
    for file_name in os.listdir(OUT_TMP):
        full_file_name = os.path.join(OUT_TMP, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, OUT)

    for file_name in os.listdir(BIN_TMP):
        full_file_name = os.path.join(BIN_TMP, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, BIN)

if __name__ == "__main__":
    os.umask(0)
    try:
        copy_src_files()
    except Exception as e:
        # Ensure we emit an OUT_FILE with a non-zero return code so callers
        # can detect the failure programmatically.
        write_meta(1)
        print(f"Error occurred while copying source files: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        compile()
    except Exception as e:
        # If compile() raised before writing OUT_FILE, ensure we still write
        # a meta file with a non-zero return code.
        write_meta(1)
        print(f"Error occurred while compiling: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        copy_out_files()
    except Exception as e:
        # On failure copying outputs, still try to emit a meta file.
        write_meta(1)
        print(f"Error occurred while copying output files: {e}", file=sys.stderr)
        sys.exit(1)
