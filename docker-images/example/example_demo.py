import subprocess
import shutil
import time

exmp_path = r".\\docker-images\example"
# comp_path = r".\\docker-images\compilers\python-compiler"
comp_path = r".\\docker-images\compilers\rust-compiler"
exec_path = r".\\docker-images\exec-python"
# exec_path = r".\\docker-images\exec"

exec_in = exmp_path+"\\exec-in"
exec_out = exmp_path+"\\exec-out"
comp_in = exmp_path+"\\comp-in"
comp_out = exmp_path+"\\comp-out"

comp_command = [
    "docker", "run", 
    # "--rm",
    '--cpus=1.0',
    # '--no-new-privileges',
    "-v", f"{comp_in}:/data/in:ro",
    "-v", f"{comp_out}:/data/out",
    "comp"
]
exec_command = [
    "docker", "run", "--rm",
    # "--rm",
    '--cpus=1.0',
    # '--no-new-privileges',
    "-v", f"{exec_in}:/data/in:ro",
    "-v", f"{exec_out}:/data/out",
    "exec"
]

# exit(1)

subprocess.run(["docker", "build", "-t", "exec", exec_path], check=True)
subprocess.run(["docker", "build", "-t", "comp", comp_path], check=True)


start_time = time.time()
subprocess.run(comp_command, check=True)
print("\n------------------------")
print(f" Compilation time: {round(time.time() - start_time, 2)}")

shutil.copy(comp_out+"\\program", exec_in) 

start_time = time.time()
subprocess.run(exec_command, check=True)
print(f" Execution time: {round(time.time() - start_time, 2)}")
print("------------------------\n")
