import subprocess
import sys
import os
import logging
import time
import json
import judge

logger = logging.getLogger("JUDGE")

def main():
    #logging
    logging.basicConfig(
        level=logging.DEBUG if os.environ.get("LOGS")=="on" else logging.ERROR,
        format="[%(name)s] %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)] 
    )
    
    #copying and running
    start_time = time.time()
    
    for file in os.listdir(os.getenv('IN')):
        if file.endswith('.out'):
            program_process = subprocess.Popen(["python", "judge.py", file.split('.')[0]])
            program_process.wait()
    
    # subprocess.run(f"cp /tmp/out/* {os.getenv('OUT')}", shell=True)
    
    logger.info(f"judge.py execution time: {round(time.time() - start_time, 2)}")

if __name__ == "__main__":
    main()