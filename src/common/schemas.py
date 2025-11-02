from pydantic import BaseModel
from typing import Dict, List, Optional

from common.utils import size_to_string



class TestResultSchema(BaseModel):
    test_name: str = ""
    grade: bool = False
    ret_code: Optional[int] = None
    time: Optional[float] = None
    memory: Optional[float] = None
    info: Optional[str] = None



class SubmissionResultSchema(BaseModel):
    points: int = 0
    info: Optional[str] = None
    debug: Optional[str] = None
    test_results: List[TestResultSchema] = []
    
    def __str__(self) -> str:
        ret = ""
        if len(self.test_results) > 0:
            ret += "+------+------+------------+-----+\n"
            ret += "| name | time |   memory   | ret |\n"
            ret += "+------+------+------------+-----+\n"
            for result in self.test_results:
                color = 131
                if result.grade:
                    color = 65
                if result.ret_code != 0:
                    color = 173
                ret += f"|\033[48;5;{color}m\033[38;5;232m {result.test_name:>4} | "
                if result.time is None or result.memory is None or result.ret_code is None or result.info is None:
                    ret += f"     |            |     |\n"
                else:
                    ret += f"{result.time:.2f} | {size_to_string(result.memory):>10} | {result.ret_code:>3} \033[0m| {result.info[:1000]}\n"
            ret += "+------+------+------------+-----+\n"
            ret += "| " + f"points: {self.points}".center(30) + " |\n"
            ret += "+--------------------------------+"
        else:
            ret += "+-----------------------+\n"
            ret += "|   compilation error   |\n"
            ret += "+-----------------------+"
        if self.info:
            ret += "\n\033[33mDebug info\033[0m: " + self.info[:-1]
        return ret



class TestSpecificationSchema(BaseModel):
    test_name: str = ""
    time_limit: float = 2
    total_memory_limit: int = 256*1024*1024  # 256 MB
    stack_size_limit: Optional[int] = None



class ProblemSpecificationSchema(BaseModel):
    id: str
    tests: List[TestSpecificationSchema] = []

    def __str__(self) -> str:
        ret = ""
        if len(self.tests) > 0:
            ret += f"+------+-------------------+\n"
            ret += f"|      |{'limits'.center(19)}|\n"
            ret += f"+------+------+------------+\n"
            ret += f"| name | time |   memory   |\n"
            ret += f"+------+------+------------+\n"
            for test in self.tests:
                ret += f"| {test.test_name:>4} | "
                ret += f"{test.time_limit:.2f} | {size_to_string(test.total_memory_limit):>10} |\n"
            ret += f"+------+------+------------+"
        return ret



class SubmissionSchema(BaseModel):
    id: str
    comp_image: str
    mainfile: Optional[str] = None
    submitted_by: Optional[str] = None
    problem_specification: ProblemSpecificationSchema
    


class SubmissionGuiSchema(BaseModel):
    submission_id: str
    problem_id: str
    student_id: str



class VolumeMappingSchema(BaseModel):
    host_path: str
    container_path: str
    read_only: bool = True
    def key(self) -> str:
        return self.host_path
    def value(self) -> Dict[str, str]:
        return {
            "bind": self.container_path,
            "mode": "ro" if self.read_only else "rw"
        }


class ExecOutputSchema(BaseModel):
    return_code: int
    signal: Optional[int] = None
    user_time: Optional[float] = None
    total_memory: Optional[int] = None


class JudgeOutputSchema(BaseModel):
    grade: bool = False
    info: Optional[str] = None
