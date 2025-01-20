import os
import shutil

output_folder_path = "docker-images/example/exec-in/"
comp_out_path = "docker-images/example/comp-out"
exec_out_path = "docker-images/example/exec-out"

if os.path.exists(comp_out_path):
    shutil.rmtree(comp_out_path)
os.makedirs(comp_out_path)

if os.path.exists(exec_out_path):
    shutil.rmtree(exec_out_path)
os.makedirs(exec_out_path)

if os.path.exists(output_folder_path):
    shutil.rmtree(output_folder_path)
os.makedirs(output_folder_path)

for i in range(20):
    in_file_name = f"{output_folder_path}{i}.in"
    out_file_name = f"{output_folder_path}{i}.out"
    
    in_test_data = ""
    out_test_data = ""
    n = int(2.3**i)
    print(n)

    with open(in_file_name, 'a') as file:
        file.write(f"{n}\n")
        for j in range(n):
            file.write("1\n")

    out_test_data += f"{n}\n"
    with open(out_file_name, 'w') as file:
        file.write(out_test_data)
