import subprocess
import sys
import os
import logging
import time

logger = logging.getLogger("MAIN")

def run_program(name: str):
    start_time2 = time.time()
    program_process = subprocess.Popen(
        ["python", "exec.py", name],
        stdout=subprocess.PIPE,
    )
    judge_process = subprocess.Popen(
        ["python", "judge.py", name],
        stdin=program_process.stdout,
        stdout=sys.stdout       
    )
    judge_process.wait()
    program_process.stdout.close()
    program_process.wait()
    
    logger.info("program returned code: " + str(program_process.returncode))
    logger.info("judge returned code: " + str(judge_process.returncode))
    logger.info(f"real time: {round(time.time() - start_time2, 2)}")

def main():
    logging.basicConfig(
        level=logging.DEBUG if os.environ.get("LOGS")=="on" else logging.ERROR,
        format="[%(name)s] %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)] 
    )
    start_time = time.time()
    subprocess.run(r'cp "${INPUT}"/* /tmp/in', shell=True, check=True)    
    copy_time = round(time.time() - start_time, 2)

    for name in range(20):
        run_program(str(name))
    
    subprocess.run(r"cp /tmp/out/* $OUTPUT", shell=True, check=True)
    logger.info(f"copy time: {copy_time}")
    logger.info(f"exec.py execution time: {round(time.time() - start_time, 2)}")

if __name__ == "__main__":
    main()