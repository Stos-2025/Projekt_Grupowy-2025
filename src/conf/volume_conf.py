import subprocess

volume_path = "/var/lib/docker/volumes/projektgrupowy_volume0/_data"
example_path = "./src/example"

subprocess.run(f"sudo mkdir -p {volume_path}/comp-out", shell=True, check=True) 
subprocess.run(f"sudo mkdir -p {volume_path}/comp-in", shell=True, check=True) 
subprocess.run(f"sudo cp {example_path}/comp-in/* {volume_path}/comp-in", shell=True, check=True)

subprocess.run(f"sudo mkdir -p {volume_path}/exec-out", shell=True, check=True) 
subprocess.run(f"sudo mkdir -p {volume_path}/exec-in", shell=True, check=True) 
subprocess.run(f"sudo cp {example_path}/exec-in/* {volume_path}/exec-in", shell=True, check=True)