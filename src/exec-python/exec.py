import sys
import subprocess
import resource
import json
import os
# import psutil

name = sys.argv[1]  
  
binary_path = f"{os.getenv('BIN')}/program"
input_path=f"{os.getenv('IN')}/{name}.in"

output_path=f"{os.getenv('OUT')}/{name}.stdout.out"
# output_path=f"/tmp/out/{name}.stdout.out"
error_path=f"{os.getenv('OUT')}/{name}.stderr.out"
# error_path=f"/tmp/out/{name}.stderr.out"
exec_path=f"{os.getenv('OUT')}/{name}.exec.json"
# exec_path=f"/tmp/out/{name}.exec.json"

return_code = 0
with open(input_path, "r") as input_file, open(error_path, "w") as error_file, open(exec_path, "w") as exec_file, open(output_path, "w") as output_file:
    program_process = subprocess.Popen(
        [binary_path],
        stdin=input_file,    
        stderr=error_file,
        stdout=output_file,
    )

    resource.prlimit(program_process.pid, resource.RLIMIT_CPU, (2, 2)) #todo change
    program_process.wait()

    meta = {}
    resources = resource.getrusage(resource.RUSAGE_CHILDREN)
    meta["return_code"] = program_process.returncode
    meta["user_time"] =  round(resources.ru_utime, 2)
    json.dump(meta, exec_file)
