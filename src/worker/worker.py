import os
import shutil
import subprocess
import json

def print_resoults(path: str):
    print("+----+------+-----+")
    print("| nr | time | ret |")
    print("+----+------+-----+")
    points = 0
    for j in range(20):
        with open(f"{path}/{j}.exec.json", "r") as exec_file, open(f"{path}/{j}.judge.json", "r") as judge_file:
            exec = json.load(exec_file)
            judge = json.load(judge_file)
            color = 131 
            if judge["grade"]:
                points += 1
                color = 65
            if exec["return_code"]!=0:
                color = 173
            print(f'|\033[48;5;{color}m\033[38;5;232m {j:>2} | {exec["user_time"]:.2f} | {exec["return_code"]:>3} \033[0m|', end=" ")
            print(judge["info"])    
    print("+----+------+-----+")
    print("| "+f"points: {points}".center(15)+" |")
    print("+----+------+-----+")


def init():
    for root, dirs, files in os.walk('/data', topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    
    os.makedirs('/data/bin', exist_ok=True)
    os.makedirs('/data/out', exist_ok=True)
    os.makedirs('/data/src', exist_ok=True)
    os.makedirs('/data/std', exist_ok=True)
    os.makedirs('/data/tests/in', exist_ok=True)
    os.makedirs('/data/tests/out', exist_ok=True)

    os.chmod('/data', 0o777)
    
    tmp_out = '/tmp/out'
    tmp_std = '/tmp/std'
    tmp_bin = '/tmp/bin'
    
    for dir_path in [tmp_out, tmp_std, tmp_bin]:
        if os.path.exists(dir_path):
            for file in os.listdir(dir_path):
                file_path = os.path.join(dir_path, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
    
    for item in os.listdir('/tmp'):
        src = os.path.join('/tmp', item)
        dst = os.path.join('/data', item)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)
    
    os.chmod('/data', 0o777)

def end():
    for item in os.listdir('/data/out'):
        src = os.path.join('/data/out', item)
        dst = os.path.join('/tmp/out', item)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

def run():

    print("compilation")
    compile_command = [
        'docker', 'run',
        '--rm',
        '--cpus=1.0',
        '--ulimit', 'cpu=30:30',
        '--network', 'none',
        '--security-opt', 'no-new-privileges',
        '-e', 'SRC=/data/src',
        '-e', 'OUT=/data/out',
        '-e', 'BIN=/data/bin',
        '-v', 'conf_worker_data:/data:rw',
        'comp'
    ]
    subprocess.run(compile_command)




    print("execution")
    execute_command = [
        'docker', 'run',
        '--rm',
        '--ulimit', 'cpu=30:30',
        '--network', 'none',
        '--security-opt', 'no-new-privileges',
        '-e', 'IN=/data/tests/in',
        '-e', 'OUT=/data/out',
        '-e', 'STD=/data/std',
        '-e', 'BIN=/data/bin',
        '-e', 'LOGS=on',
        '-v', 'conf_worker_data:/data:rw',
        'exec'
    ]
    subprocess.run(execute_command)


    print("judging")
    judge_command = [
        'docker', 'run',
        '--rm',
        '--ulimit', 'cpu=30:30',
        '--network', 'none',
        '--security-opt', 'no-new-privileges',
        '-e', 'IN=/data/std',
        '-e', 'OUT=/data/out',
        '-e', 'ANS=/data/tests/out',
        '-e', 'LOGS=on',
        '-v', 'conf_worker_data:/data:rw',
        'judge'
    ]
    subprocess.run(judge_command)


if __name__ == '__main__':
    print("init")
    init()
    print("run")
    run()
    print("print")
    print_resoults("/data/out")
    print("end")
    end()
