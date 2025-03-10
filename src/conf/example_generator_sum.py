import os
import shutil

exec_in_path = "src/example/exec-in/"
comp_out_path = "src/example/comp-out"
exec_out_path = "src/example/exec-out"

if os.path.exists(comp_out_path):
    shutil.rmtree(comp_out_path)
os.makedirs(comp_out_path)

if os.path.exists(exec_out_path):
    shutil.rmtree(exec_out_path)
os.makedirs(exec_out_path)

if os.path.exists(exec_in_path):
    shutil.rmtree(exec_in_path)
os.makedirs(exec_in_path)
os.makedirs(exec_in_path+"in")
os.makedirs(exec_in_path+"out")

for i in range(20):
    in_file_name = f"{exec_in_path}in/{i}.in"
    out_file_name = f"{exec_in_path}out/{i}.out"
    
    in_test_data = ""
    out_test_data = ""
    # n = 20000000//(20-i)
    n = round(2.3**i)
    print(n)

    with open(in_file_name, 'a') as file:
        file.write(f"{n}\n")
        for j in range(n):
            file.write("1\n")

    out_test_data += f"{n}\n"
    with open(out_file_name, 'w') as file:
        file.write(out_test_data if i != 10 else "67")
    
    os.chmod(in_file_name, 0o777)
    os.chmod(out_file_name, 0o777)
    os.chmod(comp_out_path, 0o777)
    os.chmod(exec_out_path, 0o777)
    os.chmod(exec_in_path, 0o777)

