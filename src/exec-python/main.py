"""
Main execution coordinator for the program execution system.

This module coordinates the execution of multiple test cases by invoking the
exec.py script for each .in file found in the input directory. It provides
logging, timing, and process management functionality.

The main execution flow:
1. Configure logging based on environment variables
2. Find all .in files in the input directory
3. Execute each test case using exec.py
4. Log execution times and results

Environment Variables:
    IN: Directory containing input files (.in)
    LOGS: Set to "on" to enable debug logging, otherwise error-only logging

Functions:
    run_program: Execute a single test case
    main: Main coordination function
"""

import subprocess
import sys
import os
import logging
import time

logger = logging.getLogger("EXEC")

def run_program(name: str) -> None:
    """
    Execute a single test case program.

    This function runs the exec.py script for a specific test case, measures
    execution time, and logs the results. It handles subprocess management
    and provides timing information for performance analysis.

    Args:
        name (str): The name of the test case (without .in extension)

    Example:
        >>> run_program("test1")
        # Executes: python exec.py test1
        # Logs: test   1 real time:  1.23
    """
    start_time2 = time.time()
    program_process = subprocess.Popen(["python", "exec.py", name])
    program_process.wait()
    logger.info(f"test {name:>3} real time:  {round(time.time() - start_time2, 2):.2f}")

def main() -> None:
    """
    Main execution coordinator function.

    This function coordinates the entire execution process:
    1. Sets file permissions (umask)
    2. Configures logging based on environment variables
    3. Discovers all test cases (.in files) in the input directory
    4. Executes each test case using run_program()
    5. Logs total execution time

    The function processes all .in files found in the directory specified
    by the IN environment variable, extracting the test name (filename without
    extension) and passing it to run_program().

    Environment Variables:
        IN: Directory path containing .in files
        LOGS: "on" for debug logging, any other value for error-only logging

    Raises:
        OSError: If the input directory cannot be accessed
        TypeError: If IN environment variable is not set

    Example:
        >>> os.environ['IN'] = '/data/inputs'
        >>> os.environ['LOGS'] = 'on'
        >>> main()
        # Processes all .in files in /data/inputs
        # Logs execution times and results
    """
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