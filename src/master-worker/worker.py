import docker
import shutil
import time
import json
import os


def run_example(build=True, compile=True):
    client = docker.from_env()

    exmp_path = r"./data"
  
    exec_in = os.path.join(exmp_path, "exec-in")
    exec_out = os.path.join(exmp_path, "exec-out")
    comp_in = os.path.join(exmp_path, "comp-in")
    comp_out = os.path.join(exmp_path, "comp-out")

    if compile:
        print("Running compilation container...")
        start_time = time.time()
        comp_container = client.containers.run(
            "comp",
            name="comp-container",
            remove=True,
            security_opt=["no-new-privileges"],
            volumes={
                comp_in: {"bind": "/data/in", "mode": "ro"},
                comp_out: {"bind": "/data/out", "mode": "rw"}
            }
        )
        print(f"Compilation time: {round(time.time() - start_time, 2)} seconds")
        shutil.copy(os.path.join(comp_out, "program"), exec_in)

    print("Starting execution container...")
    start_time = time.time()
    exec_container = client.containers.create(
        "exec",
        name="exec-container",
        remove=True,
        security_opt=["no-new-privileges"],
        volumes={
            exec_in: {"bind": "/data/in", "mode": "ro"},
            exec_out: {"bind": "/data/out", "mode": "rw"}
        }
    )
    exec_container.start()
    exec_container.wait()
    print(f"Execution time: {round(time.time() - start_time, 2)} seconds")
    for j in range(20):
        try:
            with open(f"{exec_out}/{j}.resource.json", "r") as file:
                data = json.load(file)
                print(f":{j} -> {round(data[0], 2)}s")
        except Exception as e:
            pass


if __name__ == "__main__":
    run_example()
