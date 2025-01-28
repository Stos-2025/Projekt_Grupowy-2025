#example python judge script
import sys
import logging
import os
import json
from typing import Tuple


def check_answer(answer_path: str, input_path: str) -> Tuple[bool, str]:
    info = "ok"
    line_nr = 0
    with open(answer_path, "r") as answer, open(input_path, "r") as input:
        for line in answer:
            line_nr += 1
            try:
                output_line = input.readline()
            except EOFError:
                info = f"unexpected EOF in line {line_nr}"
                return (False, info)
            

            if line.strip() != output_line.strip():
                info = f"line {line_nr} is not correct"
                return (False, info)
        #probably the output can be longer than the answer but its only example 
    return (True, info)

def main():          
    name = sys.argv[1]
    answer_path = os.getenv('ANS')+f"/{name}.out"
    input_path = os.getenv('IN')+f"/{name}.stdout.out"

    output = {}
    is_correct, info = check_answer(answer_path, input_path)
    output["grade"] = 1 if is_correct else 0
    output["info"] = info
    
    with open(f"{os.getenv('OUT')}/{name}.judge.json", "w") as judge_file:
        json.dump(output, judge_file)


if __name__ == "__main__":
    main()