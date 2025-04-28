import json
import os
import shutil
import subprocess
import sys

SRC = os.getenv("SRC")
OUT = os.getenv("OUT")
BIN = os.getenv("BIN")
SRC_TMP = "/tmp/src"
BIN_TMP = "/tmp/bin"
OUT_TMP = "/tmp/out"
DIAGNOSTIC_FILE = f"{OUT}/comp.txt"
OUT_FILE = f"{OUT}/comp.json"

def copy_src_files():
    os.makedirs(SRC_TMP, exist_ok=True)
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
    copy_src_files()
    compile()
    copy_out_files()
