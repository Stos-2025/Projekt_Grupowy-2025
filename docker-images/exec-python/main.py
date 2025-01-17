from typing import List, Tuple
import subprocess
import os
import sys
import shutil
import time

def run_program(name: str):
    print("Running program: " + name)
    program_process = subprocess.Popen(
        ["python", "exec.py", name],
        stdout=subprocess.PIPE
    )

    print("Running judge: " + name)
    judge_process = subprocess.Popen(
        ["python", "judge.py", name],
        stdin=program_process.stdout,
        stdout=sys.stdout       
    )
    

    program_process.wait()
    judge_process.wait()

    program_process.stdout.close()

    print("program: " + str(program_process.returncode))
    print("judge: " + str(judge_process.returncode))

def main():
    start_time = time.time()
    os.makedirs("/tmp/in")
    os.makedirs("/tmp/out")
    shutil.copy("/data/in/program",  "/tmp/in")
    
    for i in range(20): #todo
        run_program(str(i))
    
    subprocess.run("/bin/sh -c 'cp /tmp/out/* /data/out'", shell=True, check=True)
    # shutil.copytree("/tmp/out/",  "/data/out")
    print(f"exec.py execution time: {round(time.time() - start_time, 2)}")

if __name__ == "__main__":
    main()