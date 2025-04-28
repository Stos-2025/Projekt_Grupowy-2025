import subprocess
import sys
import os
import logging
import time

logger = logging.getLogger("EXEC")

def run_program(name: str):
    start_time2 = time.time()
    program_process = subprocess.Popen(["python", "exec.py", name])
    program_process.wait()
    logger.info(f"test {name:>3} real time:  {round(time.time() - start_time2, 2):.2f}")

def main():
    os.umask(0)
    start_time = time.time()
    
    #logging
    logging.basicConfig(
        level=logging.DEBUG if os.environ.get("LOGS")=="on" else logging.ERROR,
        format="[%(name)s] %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)] 
    )
    
    #running
    
    for file in os.listdir(os.getenv('IN')):
        if file.endswith('.in'):
            run_program(file.split('.')[0])
    
    # subprocess.run(f"cp /tmp/out/* {os.getenv('OUT')}", shell=True)
    
    logger.info(f"exec.py execution time: {round(time.time() - start_time, 2)}")

if __name__ == "__main__":
    main()