import sys
import subprocess
import resource
import json
import time
# import psutil

name = sys.argv[1]    
input_file=f"/tmp/in/{name}.in"
error_file=f"/tmp/out/{name}.stderr.out"
resources_file=f"/tmp/out/{name}.exec.json"

return_code = 0
with open(input_file, "r") as in_file, open(error_file, "w") as error_file, open(resources_file, "w") as exec_file:
    program_process = subprocess.Popen(
        ["/tmp/in/program"],
        stdin=in_file,    
        stderr=error_file,
        stdout=sys.stdout,
    )

    resource.prlimit(program_process.pid, resource.RLIMIT_CPU, (2, 2)) #todo change
    program_process.wait()


    meta = {}
    resources = resource.getrusage(resource.RUSAGE_CHILDREN)
    meta["return_code"] = program_process.returncode
    meta["user_time"] =  round(resources.ru_utime, 2)
    json.dump(meta, exec_file)
