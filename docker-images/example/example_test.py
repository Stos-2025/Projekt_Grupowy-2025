from example_demo import run_example
import json
import matplotlib.pyplot as plt

exec_out_path = "docker-images/example/exec-out"

times = []
n = 5

for i in range(n):
    run_example(False, False)
    times.append([])
    for j in range(20):
        with open(f"{exec_out_path}/{j}.resource.json", "r") as file:
            try:
                data = json.load(file)
                times[i].append(round(data[0], 2))
            except Exception as e:
                pass
                # times[i].append(0)
                # exit(1)
               

print(times)
plt.plot([i[17] for i in times])
plt.title('cpu user time test 17')
plt.show()
print(times)

for i in range(15, 20):
    plt.plot([j[i] for j in times], label=f'cpu user time test {i}')


plt.xlabel('n')
plt.ylabel('t')

plt.legend()
plt.show()
