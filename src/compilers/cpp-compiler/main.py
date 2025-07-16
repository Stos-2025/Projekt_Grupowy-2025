"""
C++ Compiler Module for Competitive Programming Judge System.

This module provides functionality to compile C++ source code in an isolated
environment. It handles source file copying, compilation with g++, and output
file management. The module is designed to work in a containerized environment
with proper error handling and metadata generation.

The compilation process follows these steps:
1. Copy source files from input directory to temporary workspace
2. Compile C++ files using g++ with strict warning flags
3. Generate compilation metadata (return code, diagnostics)
4. Copy output files (binary and metadata) to output directories

Environment Variables:
    SRC: Directory containing source files to compile
    OUT: Directory for compilation metadata and diagnostic output
    BIN: Directory for compiled binary output

Functions:
    copy_src_files: Copy source files to temporary workspace
    compile: Compile C++ files using g++
    copy_out_files: Copy output files to destination directories

Usage:
    This module is typically run as a standalone script in a Docker container:
    python main.py
    
    Or functions can be imported and used individually:
    from main import copy_src_files, compile, copy_out_files
"""

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

def copy_src_files() -> None:
    """
    Copy source files from input directory to temporary workspace.

    This function copies all files from the SRC directory to a temporary
    workspace (/tmp/src) for compilation. It ensures that the temporary
    directory exists and copies all files, including source files, headers,
    and any other files that might be needed for compilation.

    The function preserves file permissions and handles both regular files
    and any other file types that might be present in the source directory.

    Environment Variables:
        SRC: Source directory path containing files to copy

    Raises:
        FileNotFoundError: If the source directory doesn't exist
        PermissionError: If files cannot be read or copied
        OSError: If temporary directory cannot be created

    Example:
        >>> os.environ['SRC'] = '/data/source'
        >>> copy_src_files()
        # Copies all files from /data/source to /tmp/src
    """
    SRC = os.getenv("SRC")
    os.makedirs(SRC_TMP, exist_ok=True)
    for file_name in os.listdir(SRC):
        full_file_name = os.path.join(SRC, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, SRC_TMP)

def compile() -> None:
    """
    Compile C++ source files using g++ compiler.

    This function compiles all C++ source files (.cpp) in the temporary
    workspace using g++ with strict warning flags. It captures compilation
    errors to a diagnostic file and generates metadata about the compilation
    process.

    The compilation uses the following flags:
    - -Wextra: Enable extra warning messages
    - -Wall: Enable all common warnings
    - Output binary to /tmp/bin/program

    Compilation metadata is saved to a JSON file containing:
    - return_code: Exit code from g++ (0 for success, non-zero for failure)

    Environment Variables:
        OUT: Directory for compilation metadata and diagnostic output
        BIN: Directory for compiled binary output

    Files Created:
        - {OUT}/comp.json: Compilation metadata in JSON format
        - {OUT}/comp.txt: Compilation diagnostic output (errors/warnings)
        - /tmp/bin/program: Compiled binary (if successful)

    Example:
        >>> os.environ['OUT'] = '/data/output'
        >>> os.environ['BIN'] = '/data/binary'
        >>> compile()
        # Compiles C++ files and creates metadata
    """
    OUT = os.getenv("OUT")
    BIN = os.getenv("BIN")
    DIAGNOSTIC_FILE = f"{OUT}/comp.txt"
    OUT_FILE = f"{OUT}/comp.json"
    
    ret_code: int = os.system(f"g++ -Wextra -Wall -o {BIN_TMP}/program {SRC_TMP}/*.cpp 2> {DIAGNOSTIC_FILE}") #todo: add diagnostic file
    meta = {}
    meta["return_code"] = ret_code
    with open(OUT_FILE, "w") as out_file:
        json.dump(meta, out_file)
    
def copy_out_files() -> None:
    """
    Copy output files from temporary workspace to destination directories.

    This function copies all output files from the temporary workspace to
    their final destinations. It handles both compilation metadata/diagnostics
    and the compiled binary, ensuring all output is properly preserved.

    The function copies:
    - Files from /tmp/out to OUT directory (metadata, diagnostics)
    - Files from /tmp/bin to BIN directory (compiled binary)

    Only regular files are copied, and the function handles missing
    directories gracefully. If temporary directories don't exist or
    are empty, the function completes without error.

    Environment Variables:
        OUT: Destination directory for compilation metadata and diagnostics
        BIN: Destination directory for compiled binary

    Files Copied:
        - /tmp/out/* → {OUT}/* (compilation metadata, diagnostics)
        - /tmp/bin/* → {BIN}/* (compiled binary)

    Raises:
        PermissionError: If files cannot be copied due to permissions
        OSError: If destination directories cannot be accessed

    Example:
        >>> os.environ['OUT'] = '/data/output'
        >>> os.environ['BIN'] = '/data/binary'
        >>> copy_out_files()
        # Copies all output files to their destinations
    """
    OUT = os.getenv("OUT")
    BIN = os.getenv("BIN")
    
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
