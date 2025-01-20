from add import sum

def main():
    n = int(input())
    total = 0
    for _ in range(n):
        number = int(input())
        total = sum(total, number)
    print(total)

if __name__ == "__main__":
    main()
