#!/usr/bin/env python3

import json
import os
import shutil
import subprocess
import sys

SRC: str = os.environ["SRC"]
OUT: str = os.environ["OUT"]
BIN: str = os.environ["BIN"]

SRC_TMP: str = "/tmp/src"
BIN_TMP: str = "/tmp/bin"
OUT_TMP: str = "/tmp/out"
DIAGNOSTIC_FILE: str = f"{OUT}/comp.txt"
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
    ret_code: int = os.system(f"g++ -Wextra -Wall -o {BIN_TMP}/program {SRC_TMP}/*.cpp 2> {DIAGNOSTIC_FILE}") #todo: add diagnostic file
    meta = {}
    meta["return_code"] = ret_code
    with open(OUT_FILE, "w") as out_file:
        json.dump(meta, out_file)
    
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
        print(f"Error occurred while copying source files: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        compile()
    except Exception as e:
        print(f"Error occurred while compiling: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        copy_out_files()
    except Exception as e:
        print(f"Error occurred while copying output files: {e}", file=sys.stderr)
        sys.exit(1)
