import sys
import subprocess
import resource
import time

name = sys.argv[1]    
input_file=f"/data/in/{name}.in"
error_file=f"/tmp/out/{name}.stderr.out"

with open(input_file, "r") as infile, open(error_file, "w") as errfile:
    program_process = subprocess.Popen(
        ["/tmp/in/program"],
        stdin=infile,    
        stderr=errfile,
        stdout=sys.stdout
    )
    resource.prlimit(program_process.pid, resource.RLIMIT_CPU, (2, 2))
    
    program_process.wait() 
    
    errfile.write(str(resource.getrusage(resource.RUSAGE_CHILDREN)))   
    