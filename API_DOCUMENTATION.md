# API Documentation

## Overview

This document provides comprehensive API documentation for the competitive programming judge system. The system consists of several modules that work together to compile, execute, and evaluate program submissions.

## Architecture

The system follows a containerized architecture with the following components:

- **Compiler**: Compiles source code (C++) in isolated environment
- **Executor**: Runs compiled programs with resource limits
- **Judge**: Evaluates program output against expected results
- **Demo**: Orchestrates the complete pipeline

## Module: judge.py

### Functions

#### `check_answer(answer_path: str, input_path: str) -> Tuple[bool, str]`

Compare program output with expected answer line by line.

**Parameters:**
- `answer_path` (str): Path to the file containing expected answer
- `input_path` (str): Path to the file containing program output

**Returns:**
- `Tuple[bool, str]`: Success status and descriptive message

**Example:**
```python
result, info = check_answer("expected.txt", "output.txt")
if result:
    print("Output is correct!")
else:
    print(f"Output is incorrect: {info}")
```

#### `check_exec(exec_path: str) -> Tuple[bool, str]`

Validate program execution results from execution metadata.

**Parameters:**
- `exec_path` (str): Path to the JSON file containing execution metadata

**Returns:**
- `Tuple[bool, str]`: Success status and descriptive message

**Example:**
```python
result, info = check_exec("program.exec.json")
if result:
    print("Program executed successfully")
else:
    print(f"Program execution failed: {info}")
```

#### `check_comp(comp_path: str) -> Tuple[bool, str]`

Validate compilation results from compilation metadata.

**Parameters:**
- `comp_path` (str): Path to the JSON file containing compilation metadata

**Returns:**
- `Tuple[bool, str]`: Success status and descriptive message

**Example:**
```python
result, info = check_comp("program.comp.json")
if result:
    print("Compilation successful")
else:
    print(f"Compilation failed: {info}")
```

#### `check(name: str) -> None`

Perform complete evaluation of a program submission.

**Parameters:**
- `name` (str): Base name of the test case (without file extension)

**Environment Variables:**
- `ANS`: Directory path containing expected answer files
- `IN`: Directory path containing program output files
- `OUT`: Directory path for writing judge results

**Example:**
```python
os.environ['ANS'] = '/path/to/answers'
os.environ['IN'] = '/path/to/outputs'
os.environ['OUT'] = '/path/to/results'
check("test1")  # Evaluates test case "test1"
```

## Module: exec-python

### Script: exec.py

Executes compiled programs with resource limits and captures output.

**Command Line Usage:**
```bash
python exec.py <test_name>
```

**Environment Variables:**
- `BIN`: Directory containing the compiled program binary
- `IN`: Directory containing input files (.in)
- `STD`: Directory for standard output/error files
- `OUT`: Directory for execution metadata (.exec.json)

**Resource Limits:**
- CPU time: 2 seconds
- Memory: Monitored via rusage

**Output Files:**
- `{test_name}.stdout.out`: Program standard output
- `{test_name}.stderr.out`: Program standard error
- `{test_name}.exec.json`: Execution metadata

### Script: main.py

#### `run_program(name: str) -> None`

Execute a single test case program.

**Parameters:**
- `name` (str): The name of the test case (without .in extension)

#### `main() -> None`

Main execution coordinator function.

**Environment Variables:**
- `IN`: Directory path containing .in files
- `LOGS`: "on" for debug logging, any other value for error-only logging

## Module: compilers/cpp-compiler

### Functions

#### `copy_src_files() -> None`

Copy source files from input directory to temporary workspace.

**Environment Variables:**
- `SRC`: Source directory path containing files to copy

#### `compile() -> None`

Compile C++ source files using g++ compiler.

**Compilation Flags:**
- `-Wextra`: Enable extra warning messages
- `-Wall`: Enable all common warnings

**Environment Variables:**
- `OUT`: Directory for compilation metadata and diagnostic output
- `BIN`: Directory for compiled binary output

**Output Files:**
- `comp.json`: Compilation metadata
- `comp.txt`: Compilation diagnostic output

#### `copy_out_files() -> None`

Copy output files from temporary workspace to destination directories.

**Environment Variables:**
- `OUT`: Destination directory for compilation metadata and diagnostics
- `BIN`: Destination directory for compiled binary

## Module: example/demo.py

### Functions

#### `print_resoults(path: str) -> Tuple[int, str]`

Format and display test execution results in a table.

**Parameters:**
- `path` (str): Directory path containing .exec.json and .judge.json files

**Returns:**
- `Tuple[int, str]`: Total points scored and formatted table string

**Color Coding:**
- Green (65): Successful test case
- Red (131): Failed test case
- Orange (173): Runtime error

#### `run_example(build: bool = True, compile: bool = True, logs: bool = True) -> None`

Execute the complete competitive programming judge pipeline.

**Parameters:**
- `build` (bool): Whether to build Docker images before running
- `compile` (bool): Whether to compile source code
- `logs` (bool): Whether to enable debug logging

**Pipeline Phases:**
1. Compilation: Compiles source code using cpp-compiler
2. Execution: Runs compiled program with test inputs
3. Judging: Evaluates output against expected results

## Module: conf/generators

### Script: example_generator_sum.py

Generates test data for sum problems.

**Test Case Structure:**
- Input: First line contains n, followed by n lines each containing "1"
- Output: Single line containing the sum (equals n)

**Formula:** `n = round(2.3^i)` for exponential growth

**Test Cases:** 22 test cases (0.in to 21.in)

### Script: example_generator_echo.py

Generates test data for echo problems.

**Test Case Structure:**
- Input: Single line containing n
- Output: n lines, each containing "1"

**Formula:** `n = 1000000//(20-i)` for linear decrease

**Test Cases:** 20 test cases (0.in to 19.in)

## Error Handling

### Common Error Types

1. **FileNotFoundError**: Missing input files or directories
2. **PermissionError**: Insufficient file or directory permissions
3. **TimeoutError**: Program execution exceeds time limits
4. **JSONDecodeError**: Malformed metadata files
5. **subprocess.CalledProcessError**: Docker command failures

### Error Recovery

The system is designed to be resilient:
- Missing files are handled gracefully
- Compilation failures are captured and reported
- Runtime errors are detected and logged
- Resource limits prevent system overload

## Security Considerations

### Docker Security

- **Network isolation**: `--network none`
- **Privilege restrictions**: `--security-opt no-new-privileges`
- **Resource limits**: CPU and memory constraints
- **Read-only mounts**: Input files mounted read-only

### File System Security

- **Temporary directories**: Isolated workspaces
- **Permission management**: Controlled file access
- **Sandboxing**: Containerized execution environment

## Performance Monitoring

### Metrics Collected

- **Compilation time**: Time spent compiling source code
- **Execution time**: Program runtime (user time)
- **Memory usage**: Peak memory consumption
- **Return codes**: Exit status of all phases

### Performance Tuning

- **Resource limits**: Adjustable CPU and memory limits
- **Parallel execution**: Multiple test cases can run concurrently
- **Caching**: Docker image caching for faster builds

## Usage Examples

### Basic Usage

```python
# Run complete pipeline
from demo import run_example
run_example(build=True, compile=True, logs=True)
```

### Individual Components

```python
# Judge a specific test case
from judge import check
import os

os.environ['ANS'] = '/path/to/answers'
os.environ['IN'] = '/path/to/outputs'
os.environ['OUT'] = '/path/to/results'
check("test1")
```

### Generate Test Data

```bash
# Generate sum test cases
python src/conf/example_generator_sum.py

# Generate echo test cases
python src/conf/example_generator_echo.py
```

## Configuration

### Environment Variables

| Variable | Module | Purpose |
|----------|--------|---------|
| `SRC` | Compiler | Source code directory |
| `OUT` | Compiler/Judge | Output directory |
| `BIN` | Compiler/Executor | Binary directory |
| `IN` | Executor/Judge | Input directory |
| `STD` | Executor | Standard I/O directory |
| `ANS` | Judge | Expected answers directory |
| `LOGS` | All | Logging level |

### Docker Configuration

```yaml
# Resource limits
ulimit:
  cpu: 30:30
  
# Security options
security_opt:
  - no-new-privileges
  
# Network
network: none

# Volume mounts
volumes:
  - "./input:/data/in:ro"
  - "./output:/data/out"
```

## Testing

### Unit Tests

The system includes comprehensive unit tests:
- `test_judge.py`: Tests for judge module
- `test_exec_python.py`: Tests for execution module
- `test_compiler.py`: Tests for compiler module
- `test_generators.py`: Tests for test data generators
- `test_demo.py`: Tests for demo functionality

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test module
python -m pytest tests/test_judge.py -v

# Run with coverage
python -m pytest tests/ --cov=src/
```

### Test Coverage

The test suite covers:
- **Functionality**: All major functions and methods
- **Edge cases**: Empty files, malformed data, missing files
- **Error conditions**: Network errors, permission issues, timeouts
- **Integration**: Complete pipeline workflows

## Troubleshooting

### Common Issues

1. **Docker not found**: Ensure Docker is installed and running
2. **Permission denied**: Check file permissions and Docker access
3. **Port conflicts**: Verify no conflicting services
4. **Resource limits**: Adjust CPU/memory limits if needed

### Debug Mode

Enable debug logging:
```bash
export LOGS=on
python demo.py
```

### Log Files

- Compilation logs: `comp.txt`
- Execution logs: `*.stderr.out`
- System logs: Console output with debug enabled

## Contributing

### Code Style

- Follow PEP 8 Python style guidelines
- Use type hints for function parameters and return values
- Include comprehensive docstrings
- Add unit tests for new functionality

### Testing Requirements

- All new functions must have unit tests
- Test coverage should be maintained above 80%
- Integration tests for new workflows
- Error handling tests for edge cases

## License

This project is licensed under the terms specified in the LICENSE file.