from typing import List, Tuple
import subprocess
import resource

def executeCode(code: List[str], input: str) -> Tuple[int, str, str]:
    result = subprocess.run(
        ['python', '-c', code[0]], #todo: kod do skompilowania
        capture_output=True,
        text=True,
        input=input
    )
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    max_memory = usage.ru_maxrss
    print(usage)
    return result.returncode, result.stdout, str(usage)+result.stderr

#for testing only
def main():
    code: str = """
name = input('Enter your name: ')
print(f'Hello {name}!')
    """
    input: str = "Damian"
    print(executeCode([code], input))

if __name__ == "__main__":
    main()
