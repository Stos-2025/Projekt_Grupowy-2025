#example python judge script
import sys
import logging
import os
import json

logger = logging.getLogger("JUDGE")
info = "ok"

def check_answer(answer_file: str) -> bool:
    global info
    line_nr = 0
    with open(answer_file, "r") as file:
        for line in file:
            line_nr += 1

            try:
                program_output_line = input()
            except EOFError:
                info = f"unexpected EOF in line {line_nr}"
                logger.info(info)
                return False
            
            if line.strip() != program_output_line.strip():
                info = f"line {line_nr} is not correct"
                logger.info(info)
                return False
    return True

def main():          
    name = sys.argv[1]
    logging.basicConfig(
        level=logging.DEBUG if os.environ.get("LOGS")=="on" else logging.ERROR,
        format="\t[%(name)s] %(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)] 
    )
    logger.info(f"test {name} is starting")
    answer_file=f"/tmp/in/{name}.out"
    
    output = {}
    output["grade"] = 1 if check_answer(answer_file) else 0
    output["info"] = info
    
    with open(f"/tmp/out/{name}.judge.json", "w") as judge_file:
        json.dump(output, judge_file)

    logger.info(f"test {name} was successfully tested")

if __name__ == "__main__":
    main()