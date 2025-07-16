"""
Comprehensive unit tests for the judge module.

This module contains detailed tests for all functions in the judge.py module,
including edge cases, error conditions, and input validation.
"""

import pytest
import json
import os
import tempfile
import shutil
from unittest.mock import patch, mock_open, MagicMock
import sys

# Add the src directory to the path for importing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src/judge'))

import judge


class TestCheckAnswer:
    """Test cases for the check_answer function."""

    def test_check_answer_identical_content(self, tmp_path):
        """Test check_answer with identical answer and input files."""
        # Create test files
        answer_file = tmp_path / "answer.txt"
        input_file = tmp_path / "input.txt"
        
        content = "Hello World\n42\nTest Line"
        answer_file.write_text(content)
        input_file.write_text(content)
        
        result, info = judge.check_answer(str(answer_file), str(input_file))
        
        assert result is True
        assert info == "ok"

    def test_check_answer_with_whitespace_differences(self, tmp_path):
        """Test check_answer handles whitespace differences correctly."""
        answer_file = tmp_path / "answer.txt"
        input_file = tmp_path / "input.txt"
        
        answer_file.write_text("  Hello World  \n  42  \n")
        input_file.write_text("Hello World\n42\n")
        
        result, info = judge.check_answer(str(answer_file), str(input_file))
        
        assert result is True
        assert info == "ok"

    def test_check_answer_different_content(self, tmp_path):
        """Test check_answer with different content."""
        answer_file = tmp_path / "answer.txt"
        input_file = tmp_path / "input.txt"
        
        answer_file.write_text("expected line\n")
        input_file.write_text("actual line\n")
        
        result, info = judge.check_answer(str(answer_file), str(input_file))
        
        assert result is False
        assert "line 1 is not correct" in info
        assert "expected expected line" in info
        assert "but got actual line" in info

    def test_check_answer_input_shorter_than_answer(self, tmp_path):
        """Test check_answer when input file is shorter than answer file."""
        answer_file = tmp_path / "answer.txt"
        input_file = tmp_path / "input.txt"
        
        answer_file.write_text("line1\nline2\nline3\n")
        input_file.write_text("line1\nline2\n")
        
        result, info = judge.check_answer(str(answer_file), str(input_file))
        
        assert result is False
        assert "line 3 is not correct" in info
        assert "expected line3 but got" in info

    def test_check_answer_empty_files(self, tmp_path):
        """Test check_answer with empty files."""
        answer_file = tmp_path / "answer.txt"
        input_file = tmp_path / "input.txt"
        
        answer_file.write_text("")
        input_file.write_text("")
        
        result, info = judge.check_answer(str(answer_file), str(input_file))
        
        assert result is True
        assert info == "ok"

    def test_check_answer_only_newlines(self, tmp_path):
        """Test check_answer with files containing only newlines."""
        answer_file = tmp_path / "answer.txt"
        input_file = tmp_path / "input.txt"
        
        answer_file.write_text("\n\n\n")
        input_file.write_text("\n\n\n")
        
        result, info = judge.check_answer(str(answer_file), str(input_file))
        
        assert result is True
        assert info == "ok"

    def test_check_answer_file_not_found(self):
        """Test check_answer behavior when files don't exist."""
        with pytest.raises(FileNotFoundError):
            judge.check_answer("nonexistent_answer.txt", "nonexistent_input.txt")


class TestCheckExec:
    """Test cases for the check_exec function."""

    def test_check_exec_success(self, tmp_path):
        """Test check_exec with successful execution."""
        exec_file = tmp_path / "exec.json"
        exec_data = {
            "return_code": 0,
            "user_time": 1.5,
            "memory": 500000
        }
        exec_file.write_text(json.dumps(exec_data))
        
        result, info = judge.check_exec(str(exec_file))
        
        assert result is True
        assert info == "ok"

    def test_check_exec_non_zero_return_code(self, tmp_path):
        """Test check_exec with non-zero return code."""
        exec_file = tmp_path / "exec.json"
        exec_data = {
            "return_code": 1,
            "user_time": 1.5,
            "memory": 500000
        }
        exec_file.write_text(json.dumps(exec_data))
        
        result, info = judge.check_exec(str(exec_file))
        
        assert result is False
        assert "program exited with return code 1" in info

    def test_check_exec_negative_return_code(self, tmp_path):
        """Test check_exec with negative return code (signal termination)."""
        exec_file = tmp_path / "exec.json"
        exec_data = {
            "return_code": -9,
            "user_time": 2.0,
            "memory": 1000000
        }
        exec_file.write_text(json.dumps(exec_data))
        
        result, info = judge.check_exec(str(exec_file))
        
        assert result is False
        assert "program exited with return code -9" in info

    def test_check_exec_malformed_json(self, tmp_path):
        """Test check_exec with malformed JSON."""
        exec_file = tmp_path / "exec.json"
        exec_file.write_text("invalid json content")
        
        with pytest.raises(json.JSONDecodeError):
            judge.check_exec(str(exec_file))

    def test_check_exec_missing_return_code(self, tmp_path):
        """Test check_exec with missing return_code field."""
        exec_file = tmp_path / "exec.json"
        exec_data = {
            "user_time": 1.5,
            "memory": 500000
        }
        exec_file.write_text(json.dumps(exec_data))
        
        with pytest.raises(KeyError):
            judge.check_exec(str(exec_file))

    def test_check_exec_file_not_found(self):
        """Test check_exec behavior when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            judge.check_exec("nonexistent_exec.json")


class TestCheckComp:
    """Test cases for the check_comp function."""

    def test_check_comp_success(self, tmp_path):
        """Test check_comp with successful compilation."""
        comp_file = tmp_path / "comp.json"
        comp_data = {"return_code": 0}
        comp_file.write_text(json.dumps(comp_data))
        
        result, info = judge.check_comp(str(comp_file))
        
        assert result is True
        assert info == "ok"

    def test_check_comp_failure(self, tmp_path):
        """Test check_comp with compilation failure."""
        comp_file = tmp_path / "comp.json"
        comp_data = {"return_code": 1}
        comp_file.write_text(json.dumps(comp_data))
        
        result, info = judge.check_comp(str(comp_file))
        
        assert result is False
        assert "compilation failed with return code 1" in info

    def test_check_comp_missing_file(self):
        """Test check_comp when file doesn't exist."""
        result, info = judge.check_comp("nonexistent_comp.json")
        
        assert result is True
        assert info == "ok"

    def test_check_comp_malformed_json(self, tmp_path):
        """Test check_comp with malformed JSON."""
        comp_file = tmp_path / "comp.json"
        comp_file.write_text("invalid json")
        
        result, info = judge.check_comp(str(comp_file))
        
        assert result is True
        assert info == "ok"

    def test_check_comp_missing_return_code(self, tmp_path):
        """Test check_comp with missing return_code field."""
        comp_file = tmp_path / "comp.json"
        comp_data = {"other_field": "value"}
        comp_file.write_text(json.dumps(comp_data))
        
        result, info = judge.check_comp(str(comp_file))
        
        assert result is True
        assert info == "ok"


class TestCheck:
    """Test cases for the check function."""

    def setup_method(self):
        """Setup test environment variables."""
        self.original_env = {}
        env_vars = ['ANS', 'IN', 'OUT']
        for var in env_vars:
            self.original_env[var] = os.environ.get(var)

    def teardown_method(self):
        """Restore original environment variables."""
        for var, value in self.original_env.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]

    def test_check_full_success(self, tmp_path):
        """Test check function with successful compilation, execution, and judging."""
        # Setup environment
        ans_dir = tmp_path / "ans"
        in_dir = tmp_path / "in"
        out_dir = tmp_path / "out"
        
        ans_dir.mkdir()
        in_dir.mkdir()
        out_dir.mkdir()
        
        os.environ['ANS'] = str(ans_dir)
        os.environ['IN'] = str(in_dir)
        os.environ['OUT'] = str(out_dir)
        
        # Create test files
        test_name = "test1"
        
        # Answer file
        (ans_dir / f"{test_name}.out").write_text("42\n")
        
        # Program output
        (in_dir / f"{test_name}.stdout.out").write_text("42\n")
        
        # Compilation result
        comp_data = {"return_code": 0}
        (out_dir / "comp.json").write_text(json.dumps(comp_data))
        
        # Execution result
        exec_data = {"return_code": 0, "user_time": 1.0, "memory": 100000}
        (out_dir / f"{test_name}.exec.json").write_text(json.dumps(exec_data))
        
        # Run check
        judge.check(test_name)
        
        # Verify judge result
        judge_file = out_dir / f"{test_name}.judge.json"
        assert judge_file.exists()
        
        with open(judge_file, 'r') as f:
            result = json.load(f)
        
        assert result["grade"] == 1
        assert result["info"] == "ok"

    def test_check_compilation_failure(self, tmp_path):
        """Test check function with compilation failure."""
        # Setup environment
        ans_dir = tmp_path / "ans"
        in_dir = tmp_path / "in"
        out_dir = tmp_path / "out"
        
        ans_dir.mkdir()
        in_dir.mkdir()
        out_dir.mkdir()
        
        os.environ['ANS'] = str(ans_dir)
        os.environ['IN'] = str(in_dir)
        os.environ['OUT'] = str(out_dir)
        
        # Create test files
        test_name = "test1"
        
        # Answer file
        (ans_dir / f"{test_name}.out").write_text("42\n")
        
        # Program output
        (in_dir / f"{test_name}.stdout.out").write_text("42\n")
        
        # Compilation failure
        comp_data = {"return_code": 1}
        (out_dir / "comp.json").write_text(json.dumps(comp_data))
        
        # Execution result
        exec_data = {"return_code": 0, "user_time": 1.0, "memory": 100000}
        (out_dir / f"{test_name}.exec.json").write_text(json.dumps(exec_data))
        
        # Run check
        judge.check(test_name)
        
        # Verify judge result
        judge_file = out_dir / f"{test_name}.judge.json"
        assert judge_file.exists()
        
        with open(judge_file, 'r') as f:
            result = json.load(f)
        
        assert result["grade"] == 0
        assert "compilation failed" in result["info"]

    def test_check_execution_failure(self, tmp_path):
        """Test check function with execution failure."""
        # Setup environment
        ans_dir = tmp_path / "ans"
        in_dir = tmp_path / "in"
        out_dir = tmp_path / "out"
        
        ans_dir.mkdir()
        in_dir.mkdir()
        out_dir.mkdir()
        
        os.environ['ANS'] = str(ans_dir)
        os.environ['IN'] = str(in_dir)
        os.environ['OUT'] = str(out_dir)
        
        # Create test files
        test_name = "test1"
        
        # Answer file
        (ans_dir / f"{test_name}.out").write_text("42\n")
        
        # Program output
        (in_dir / f"{test_name}.stdout.out").write_text("42\n")
        
        # Compilation success
        comp_data = {"return_code": 0}
        (out_dir / "comp.json").write_text(json.dumps(comp_data))
        
        # Execution failure
        exec_data = {"return_code": 1, "user_time": 1.0, "memory": 100000}
        (out_dir / f"{test_name}.exec.json").write_text(json.dumps(exec_data))
        
        # Run check
        judge.check(test_name)
        
        # Verify judge result
        judge_file = out_dir / f"{test_name}.judge.json"
        assert judge_file.exists()
        
        with open(judge_file, 'r') as f:
            result = json.load(f)
        
        assert result["grade"] == 0
        assert "program exited with return code 1" in result["info"]

    def test_check_answer_mismatch(self, tmp_path):
        """Test check function with answer mismatch."""
        # Setup environment
        ans_dir = tmp_path / "ans"
        in_dir = tmp_path / "in"
        out_dir = tmp_path / "out"
        
        ans_dir.mkdir()
        in_dir.mkdir()
        out_dir.mkdir()
        
        os.environ['ANS'] = str(ans_dir)
        os.environ['IN'] = str(in_dir)
        os.environ['OUT'] = str(out_dir)
        
        # Create test files
        test_name = "test1"
        
        # Answer file
        (ans_dir / f"{test_name}.out").write_text("42\n")
        
        # Program output (wrong answer)
        (in_dir / f"{test_name}.stdout.out").write_text("43\n")
        
        # Compilation success
        comp_data = {"return_code": 0}
        (out_dir / "comp.json").write_text(json.dumps(comp_data))
        
        # Execution success
        exec_data = {"return_code": 0, "user_time": 1.0, "memory": 100000}
        (out_dir / f"{test_name}.exec.json").write_text(json.dumps(exec_data))
        
        # Run check
        judge.check(test_name)
        
        # Verify judge result
        judge_file = out_dir / f"{test_name}.judge.json"
        assert judge_file.exists()
        
        with open(judge_file, 'r') as f:
            result = json.load(f)
        
        assert result["grade"] == 0
        assert "line 1 is not correct" in result["info"]
        assert "expected 42" in result["info"]
        assert "but got 43" in result["info"]

    def test_check_missing_environment_variables(self):
        """Test check function with missing environment variables."""
        # Clear environment variables
        for var in ['ANS', 'IN', 'OUT']:
            if var in os.environ:
                del os.environ[var]
        
        with pytest.raises(TypeError):
            judge.check("test1")


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_very_large_files(self, tmp_path):
        """Test handling of very large files."""
        answer_file = tmp_path / "answer.txt"
        input_file = tmp_path / "input.txt"
        
        # Create large content
        large_content = "line\n" * 100000
        answer_file.write_text(large_content)
        input_file.write_text(large_content)
        
        result, info = judge.check_answer(str(answer_file), str(input_file))
        
        assert result is True
        assert info == "ok"

    def test_unicode_content(self, tmp_path):
        """Test handling of Unicode content."""
        answer_file = tmp_path / "answer.txt"
        input_file = tmp_path / "input.txt"
        
        unicode_content = "Hello 世界\nТест\n🎉\n"
        answer_file.write_text(unicode_content, encoding='utf-8')
        input_file.write_text(unicode_content, encoding='utf-8')
        
        result, info = judge.check_answer(str(answer_file), str(input_file))
        
        assert result is True
        assert info == "ok"

    def test_binary_content(self, tmp_path):
        """Test handling of binary content."""
        answer_file = tmp_path / "answer.bin"
        input_file = tmp_path / "input.bin"
        
        binary_content = b'\x00\x01\x02\x03\xff\xfe\xfd'
        answer_file.write_bytes(binary_content)
        input_file.write_bytes(binary_content)
        
        # This should raise an exception due to binary content
        with pytest.raises(UnicodeDecodeError):
            judge.check_answer(str(answer_file), str(input_file))

    def test_extremely_long_lines(self, tmp_path):
        """Test handling of extremely long lines."""
        answer_file = tmp_path / "answer.txt"
        input_file = tmp_path / "input.txt"
        
        long_line = "x" * 1000000 + "\n"
        answer_file.write_text(long_line)
        input_file.write_text(long_line)
        
        result, info = judge.check_answer(str(answer_file), str(input_file))
        
        assert result is True
        assert info == "ok"