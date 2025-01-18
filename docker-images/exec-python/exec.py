import sys
import subprocess
import resource
import json
# import psutil

name = sys.argv[1]    
input_file=f"/tmp/in/{name}.in"
error_file=f"/tmp/out/{name}.stderr.out"
resources_file=f"/tmp/out/{name}.resource.json"

return_code = 0
with open(input_file, "r") as infile, open(error_file, "w") as errfile, open(resources_file, "w") as resfile:
    program_process = subprocess.Popen(
        ["/tmp/in/program"],
        stdin=infile,    
        stderr=errfile,
        stdout=sys.stdout,
        preexec_fn=lambda: resource.setrlimit(resource.RLIMIT_CPU, (2, 2))
    )
    program_process.wait()
    return_code = program_process.returncode
    json.dump(resource.getrusage(resource.RUSAGE_CHILDREN), resfile)
    # resfile.write(str(resource.getrusage(resource.RUSAGE_CHILDREN)))   

exit(return_code)