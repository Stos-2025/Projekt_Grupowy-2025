from demo import run_example, print_resoults
import json
import matplotlib.pyplot as plt

exec_out_path = "src/example/exec-out"

times = []
n = 25

for i in range(n):
    run_example(False, False, False)
    times.append([])
    for j in range(20):
        with open(f"{exec_out_path}/{j}.exec.json", "r") as exec_file:
            exec = json.load(exec_file)
            times[i].append(exec["user_time"])

               

for i in range(15, 20):
    plt.plot([j[i] for j in times], label=f'cpu user time test {i}')


plt.xlabel('n')
plt.ylabel('t')

plt.legend()
plt.show()
