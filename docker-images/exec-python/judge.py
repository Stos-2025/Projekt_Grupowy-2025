#example python judge script
import sys
import logging

logger = logging.getLogger("JUDGE")

def check_answer(answer_file: str) -> bool:
    line_nr = 0
    with open(answer_file, "r") as file:
        for line in file:
            line_nr += 1

            try:
                program_output_line = input()
            except EOFError:
                logger.info(f"unexpected EOF in line {line_nr}")
                return False
            
            if line.strip() != program_output_line.strip():
                logger.info(f"line {line_nr} is not correct")
                return False
    return True

def main():          
    name = sys.argv[1]
    logging.basicConfig(
        level=logging.DEBUG,
        format="\t[%(name)s] %(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)] 
    )
    logger.info(f"test {name} is starting")
    answer_file=f"/tmp/in/{name}.out"
    code = 0 if check_answer(answer_file) else 1
    logger.info(f"test {name} was successfully tested with return code {code}")
    exit(code)

if __name__ == "__main__":
    main()