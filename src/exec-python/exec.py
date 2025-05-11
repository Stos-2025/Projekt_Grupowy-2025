import sys
import subprocess
import resource
import json
import os
# import psutil

name = sys.argv[1]  
  
binary_path = f"{os.getenv('BIN')}/program"
input_path=f"{os.getenv('IN')}/{name}.in"

output_path=f"{os.getenv('STD')}/{name}.stdout.out"
# output_path=f"/tmp/out/{name}.stdout.out"
error_path=f"{os.getenv('STD')}/{name}.stderr.out"
# error_path=f"/tmp/out/{name}.stderr.out"
exec_path=f"{os.getenv('OUT')}/{name}.exec.json"
# exec_path=f"/tmp/out/{name}.exec.json"

with open(input_path, "r") as input_file, open(error_path, "w") as error_file, open(output_path, "w") as output_file:
    try:
        program_process = subprocess.Popen(
            [binary_path],
            stdin=input_file,    
            stderr=error_file,
            stdout=output_file,
        )
    except FileNotFoundError as e:
        print("Compilation failed", flush=True)
        exit(1)
        
    resource.prlimit(program_process.pid, resource.RLIMIT_CPU, (2, 2)) #todo change
    program_process.wait()

    resources = resource.getrusage(resource.RUSAGE_CHILDREN)
    with open(exec_path, "w") as exec_file:
        meta = {}
        meta["return_code"] = program_process.returncode
        meta["user_time"] =  round(resources.ru_utime, 10)
        meta["memory"] =  round(resources.ru_maxrss, 10)
        # meta["memory"] = round(psutil.Process(program_process.pid).memory_info().rss / 1024, 10)
        # meta["user_time"] = round(psutil.Process(program_process.pid).cpu_times().user, 10)
        # meta["return_code"] = program_process.returncode
        # meta["memory"] = round(resources.ru_maxrss / 1024, 10)
        # meta["user_time"] = round(resources.ru_utime, 10)
        # meta["system_time"] = round(resources.ru_stime, 10)
        # meta["max_memory"] = round(resources.ru_maxrss / 1024, 10)
        # meta["page_faults"] = resources.ru_majflt + resources.ru_minflt
        # meta["voluntary_context_switches"] = resources.ru_nvcsw
        # meta["involuntary_context_switches"] = resources.ru_nivcsw
        json.dump(meta, exec_file)
