import subprocess
import shutil
import time
import json

def run_example(build = True, compile = True):
    # build = False
    exmp_path = r"./src/example"
    # comp_path = r"./src/compilers/python-compiler"
    comp_path = r"./src/compilers/cpp-compiler"
    # comp_path = r"./src/compilers/rust-compiler"
    exec_path = r"./src/exec-python"
    # exec_path = r"./src/exec-legacy"

    exec_in = exmp_path+"/exec-in"
    exec_out = exmp_path+"/exec-out"
    comp_in = exmp_path+"/comp-in"
    comp_out = exmp_path+"/comp-out" 

    comp_command = [
        "docker", "run", 
        "--rm",
        "--name", "comp-container",
        # "--cpus=1.0",
        "--security-opt", "no-new-privileges",
        "-v", f"{comp_in}:/data/in:ro",
        "-v", f"{comp_out}:/data/out",
        "comp"
    ]
    create_exec_command = [
        "docker", "create", 
        "--rm",
        "--name", "exec-container",
        # "--cpus=0.5",
        "--security-opt", "no-new-privileges",
        "-v", f"{exec_in}:/data/in:ro",
        "-v", f"{exec_out}:/data/out",
        "exec"
    ]


    # exit(1)
    if build:
        subprocess.run(["docker", "build", "--build-arg", "LOGS=on", "-t", "exec", exec_path], check=True)
        subprocess.run(["docker", "build", "-t", "comp", comp_path], check=True)

    if compile:
        start_time = time.time()
        subprocess.run(comp_command, check=True)
        print(f" Compilation time: {round(time.time() - start_time, 2)}")
        shutil.copy(comp_out+"/program", exec_in) 

    start_time = time.time()
    container_id = subprocess.run(create_exec_command)
    print(f" Starting exec container")
    subprocess.run(["docker", "start", "-i", "exec-container"], check=True)
    print(f" Execution time: {round(time.time() - start_time, 2)}")

    
    for j in range(20):
        with open(f"{exec_out}/{j}.resource.json", "r") as file:
            try:
                data = json.load(file)
                print(f":{j} -> {round(data[0], 2)}s")
            except Exception as e:
                pass
                # exit(1)

if __name__ == "__main__":
    run_example()