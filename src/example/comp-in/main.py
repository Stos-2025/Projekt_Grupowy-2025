from add import sum

def tsum():
    n = int(input())
    total = 0
    for _ in range(n):
        number = int(input())
        total = sum(total, number)
    print(total)

def echo():
    n = int(input())
    for _ in range(n):
        print("1")

if __name__ == "__main__":
    tsum()
