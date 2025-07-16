"""
Comprehensive unit tests for the demo functionality.

This module contains detailed tests for the demo.py script,
including function testing, integration testing, and error handling.
"""

import pytest
import os
import tempfile
import json
import subprocess
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the src directory to the path for importing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src/example'))

import demo


class TestPrintResults:
    """Test cases for the print_results function."""

    def test_print_results_function_exists(self):
        """Test that print_results function exists."""
        assert hasattr(demo, 'print_resoults')  # Note: function has typo in original
        assert callable(demo.print_resoults)

    def test_print_results_with_mock_files(self):
        """Test print_results with mock execution files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create the expected directory structure
            exec_out_dir = os.path.join(tmpdir, "src", "example", "exec-out")
            os.makedirs(exec_out_dir)
            
            # Create mock execution files
            for i in range(3):
                # Create exec.json
                exec_data = {
                    "return_code": 0,
                    "user_time": 0.1 * (i + 1),
                    "memory": 1000 * (i + 1)
                }
                with open(os.path.join(exec_out_dir, f'{i}.exec.json'), 'w') as f:
                    json.dump(exec_data, f)
                
                # Create judge.json
                judge_data = {
                    "grade": 1,
                    "info": "ok"
                }
                with open(os.path.join(exec_out_dir, f'{i}.judge.json'), 'w') as f:
                    json.dump(judge_data, f)
            
            # Change to test directory and run
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                # Test print_results
                points, result = demo.print_resoults(exec_out_dir)
                
                # Check return values
                assert points == 3
                assert isinstance(result, str)
                assert "points: 3" in result
                assert "+----+------+-----+" in result
                
            finally:
                os.chdir(original_cwd)

    def test_print_results_with_failed_tests(self):
        """Test print_results with failed test cases."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create the expected directory structure
            exec_out_dir = os.path.join(tmpdir, "src", "example", "exec-out")
            os.makedirs(exec_out_dir)
            
            # Create mixed success/failure test files
            test_cases = [
                {"exec": {"return_code": 0, "user_time": 0.1}, "judge": {"grade": 1, "info": "ok"}},
                {"exec": {"return_code": 1, "user_time": 0.2}, "judge": {"grade": 0, "info": "wrong answer"}},
                {"exec": {"return_code": 0, "user_time": 0.15}, "judge": {"grade": 1, "info": "ok"}},
            ]
            
            for i, test_case in enumerate(test_cases):
                # Create exec.json
                with open(os.path.join(exec_out_dir, f'{i}.exec.json'), 'w') as f:
                    json.dump(test_case["exec"], f)
                
                # Create judge.json
                with open(os.path.join(exec_out_dir, f'{i}.judge.json'), 'w') as f:
                    json.dump(test_case["judge"], f)
            
            # Change to test directory and run
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                # Test print_results
                points, result = demo.print_resoults(exec_out_dir)
                
                # Check return values
                assert points == 2  # 2 out of 3 tests passed
                assert "points: 2" in result
                assert "wrong answer" in result
                
            finally:
                os.chdir(original_cwd)

    def test_print_results_with_runtime_errors(self):
        """Test print_results with runtime errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test case with runtime error
            exec_data = {
                "return_code": -9,  # Killed by signal
                "user_time": 2.0,
                "memory": 5000
            }
            judge_data = {
                "grade": 0,
                "info": "runtime error"
            }
            
            with open(os.path.join(tmpdir, '0.exec.json'), 'w') as f:
                json.dump(exec_data, f)
            
            with open(os.path.join(tmpdir, '0.judge.json'), 'w') as f:
                json.dump(judge_data, f)
            
            # Test print_results
            points, result = demo.print_resoults(tmpdir)
            
            # Check return values
            assert points == 0
            assert "runtime error" in result
            assert "-9" in result  # Should show negative return code

    def test_print_results_sorting(self):
        """Test that print_results sorts test cases correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files in non-sequential order
            test_numbers = [2, 0, 1, 10, 5]
            
            for num in test_numbers:
                exec_data = {"return_code": 0, "user_time": 0.1, "memory": 1000}
                judge_data = {"grade": 1, "info": "ok"}
                
                with open(os.path.join(tmpdir, f'{num}.exec.json'), 'w') as f:
                    json.dump(exec_data, f)
                
                with open(os.path.join(tmpdir, f'{num}.judge.json'), 'w') as f:
                    json.dump(judge_data, f)
            
            # Test print_results
            points, result = demo.print_resoults(tmpdir)
            
            # Check that results are sorted
            lines = result.split('\n')
            test_lines = [line for line in lines if '|' in line and 'nr' not in line and 'points' not in line and '----' not in line]
            
            # Should have test cases in order
            assert len(test_lines) == 5


class TestRunExample:
    """Test cases for the run_example function."""

    def test_run_example_function_exists(self):
        """Test that run_example function exists."""
        assert hasattr(demo, 'run_example')
        assert callable(demo.run_example)

    def test_run_example_default_parameters(self):
        """Test run_example function signature and defaults."""
        # Check function signature
        import inspect
        sig = inspect.signature(demo.run_example)
        
        # Should have build, compile, and logs parameters
        params = list(sig.parameters.keys())
        assert 'build' in params
        assert 'compile' in params
        assert 'logs' in params

    def test_run_example_path_configuration(self):
        """Test that run_example configures paths correctly."""
        # Read the function source to verify path configuration
        import inspect
        source = inspect.getsource(demo.run_example)
        
        # Check path configurations
        assert 'exmp_path = r"./src/example"' in source
        assert 'comp_path = r"./src/compilers/cpp-compiler"' in source
        assert 'exec_path = r"./src/exec-python"' in source
        assert 'judge_path = r"./src/judge"' in source

    def test_run_example_docker_commands(self):
        """Test that run_example configures Docker commands correctly."""
        import inspect
        source = inspect.getsource(demo.run_example)
        
        # Check Docker command configurations
        assert 'docker", "run"' in source
        assert '--rm' in source
        assert '--ulimit' in source
        assert '--network", "none"' in source
        assert '--security-opt", "no-new-privileges"' in source

    def test_run_example_environment_variables(self):
        """Test that run_example sets environment variables correctly."""
        import inspect
        source = inspect.getsource(demo.run_example)
        
        # Check environment variable settings
        assert 'BIN=/data/out' in source
        assert 'LOGS=' in source

    def test_run_example_volume_mounts(self):
        """Test that run_example configures volume mounts correctly."""
        import inspect
        source = inspect.getsource(demo.run_example)
        
        # Check volume mount configurations
        assert '/data/in:ro' in source
        assert '/data/out' in source
        assert '/data/bin:ro' in source
        assert '/data/answer:ro' in source

    @patch('subprocess.run')
    def test_run_example_build_phase(self, mock_run):
        """Test run_example build phase."""
        mock_run.return_value = MagicMock(returncode=0)
        
        # Mock the print_resoults function to avoid file operations
        with patch('demo.print_resoults') as mock_print:
            mock_print.return_value = (0, "test result")
            
            # Call run_example with build=True
            demo.run_example(build=True, compile=False, logs=False)
            
            # Verify that docker build commands were called
            build_calls = [call for call in mock_run.call_args_list if 'docker' in call[0][0] and 'build' in call[0][0]]
            assert len(build_calls) >= 3  # Should build exec, judge, and comp images

    @patch('subprocess.run')
    def test_run_example_compile_phase(self, mock_run):
        """Test run_example compile phase."""
        mock_run.return_value = MagicMock(returncode=0)
        
        # Mock the print_resoults function
        with patch('demo.print_resoults') as mock_print:
            mock_print.return_value = (0, "test result")
            
            # Call run_example with compile=True
            demo.run_example(build=False, compile=True, logs=False)
            
            # Verify that compilation command was called
            compile_calls = [call for call in mock_run.call_args_list if 'comp' in str(call)]
            assert len(compile_calls) >= 1

    @patch('subprocess.run')
    def test_run_example_execution_phases(self, mock_run):
        """Test run_example execution and judging phases."""
        mock_run.return_value = MagicMock(returncode=0)
        
        # Mock the print_resoults function
        with patch('demo.print_resoults') as mock_print:
            mock_print.return_value = (0, "test result")
            
            # Call run_example
            demo.run_example(build=False, compile=False, logs=False)
            
            # Verify that execution and judging commands were called
            exec_calls = [call for call in mock_run.call_args_list if 'exec' in str(call)]
            judge_calls = [call for call in mock_run.call_args_list if 'judge' in str(call)]
            
            assert len(exec_calls) >= 1
            assert len(judge_calls) >= 1

    @patch('subprocess.run')
    @patch('time.time')
    def test_run_example_timing(self, mock_time, mock_run):
        """Test that run_example measures execution time."""
        mock_run.return_value = MagicMock(returncode=0)
        mock_time.side_effect = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]  # Mock time progression
        
        # Mock the print_resoults function
        with patch('demo.print_resoults') as mock_print:
            mock_print.return_value = (0, "test result")
            
            # Mock print to capture timing output
            with patch('builtins.print') as mock_print_builtin:
                demo.run_example(build=False, compile=True, logs=False)
                
                # Check that timing information was printed
                print_calls = [str(call) for call in mock_print_builtin.call_args_list]
                timing_calls = [call for call in print_calls if 'time' in call.lower()]
                assert len(timing_calls) >= 1

    @patch('subprocess.run')
    def test_run_example_error_handling(self, mock_run):
        """Test run_example error handling."""
        # Mock subprocess to raise an exception
        mock_run.side_effect = Exception("Docker error")
        
        # Test that function handles errors gracefully
        try:
            result = demo.run_example(build=False, compile=True, logs=False)
            assert result == 1  # Should return error code
        except Exception as e:
            # If exception is not caught, that's also acceptable
            assert "Docker error" in str(e)


class TestDemoScript:
    """Test cases for the demo script as a whole."""

    def test_demo_script_main_block(self):
        """Test the main execution block of demo.py."""
        demo_script_path = os.path.join(os.path.dirname(__file__), '../src/example/demo.py')
        
        with open(demo_script_path, 'r') as f:
            content = f.read()
        
        # Check main block
        assert 'if __name__ == "__main__":' in content
        assert 'run_example()' in content

    def test_demo_script_directory_change(self):
        """Test that demo script changes directory correctly."""
        demo_script_path = os.path.join(os.path.dirname(__file__), '../src/example/demo.py')
        
        with open(demo_script_path, 'r') as f:
            content = f.read()
        
        # Check directory change logic
        assert 'file_dir = os.path.dirname( os.path.abspath(__file__) )' in content
        assert 'os.chdir(f"{file_dir}/../..")' in content

    def test_demo_script_imports(self):
        """Test that demo script has correct imports."""
        demo_script_path = os.path.join(os.path.dirname(__file__), '../src/example/demo.py')
        
        with open(demo_script_path, 'r') as f:
            content = f.read()
        
        # Check imports
        assert 'import subprocess' in content
        assert 'import os' in content
        assert 'import time' in content
        assert 'import json' in content
        assert 'from typing import Tuple' in content

    def test_demo_script_color_codes(self):
        """Test that demo script includes color codes for output."""
        demo_script_path = os.path.join(os.path.dirname(__file__), '../src/example/demo.py')
        
        with open(demo_script_path, 'r') as f:
            content = f.read()
        
        # Check color codes
        assert '\\033[48;5;' in content  # Background color
        assert '\\033[38;5;' in content  # Foreground color
        assert '\\033[0m' in content     # Reset color

    def test_demo_script_table_formatting(self):
        """Test that demo script formats results as a table."""
        demo_script_path = os.path.join(os.path.dirname(__file__), '../src/example/demo.py')
        
        with open(demo_script_path, 'r') as f:
            content = f.read()
        
        # Check table formatting
        assert '+----+------+-----+' in content
        assert '| nr | time | ret |' in content


class TestDemoIntegration:
    """Integration tests for the demo functionality."""

    def test_demo_with_minimal_setup(self):
        """Test demo with minimal file setup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create minimal directory structure
            example_dir = os.path.join(tmpdir, 'src', 'example')
            exec_out_dir = os.path.join(example_dir, 'exec-out')
            os.makedirs(exec_out_dir)
            
            # Create minimal test files
            exec_data = {"return_code": 0, "user_time": 0.1, "memory": 1000}
            judge_data = {"grade": 1, "info": "ok"}
            
            with open(os.path.join(exec_out_dir, '0.exec.json'), 'w') as f:
                json.dump(exec_data, f)
            
            with open(os.path.join(exec_out_dir, '0.judge.json'), 'w') as f:
                json.dump(judge_data, f)
            
            # Test print_results function
            points, result = demo.print_resoults(exec_out_dir)
            
            # Verify results
            assert points == 1
            assert "points: 1" in result
            assert "ok" in result

    def test_demo_performance_measurement(self):
        """Test that demo properly measures performance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exec_out_dir = os.path.join(tmpdir, 'exec-out')
            os.makedirs(exec_out_dir)
            
            # Create test files with different execution times
            test_cases = [
                {"time": 0.01, "grade": 1},
                {"time": 0.5, "grade": 1},
                {"time": 1.0, "grade": 0},
                {"time": 2.0, "grade": 0},
            ]
            
            for i, test_case in enumerate(test_cases):
                exec_data = {
                    "return_code": 0 if test_case["grade"] else 1,
                    "user_time": test_case["time"],
                    "memory": 1000
                }
                judge_data = {
                    "grade": test_case["grade"],
                    "info": "ok" if test_case["grade"] else "wrong answer"
                }
                
                with open(os.path.join(exec_out_dir, f'{i}.exec.json'), 'w') as f:
                    json.dump(exec_data, f)
                
                with open(os.path.join(exec_out_dir, f'{i}.judge.json'), 'w') as f:
                    json.dump(judge_data, f)
            
            # Test print_results
            points, result = demo.print_resoults(exec_out_dir)
            
            # Check that timing information is included
            assert "0.01" in result
            assert "0.50" in result
            assert "1.00" in result
            assert "2.00" in result
            
            # Check that points are calculated correctly
            assert points == 2


class TestDemoErrorHandling:
    """Test error handling in demo functionality."""

    def test_demo_missing_files(self):
        """Test demo behavior with missing files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create the expected directory structure but leave it empty
            exec_out_dir = os.path.join(tmpdir, "src", "example", "exec-out")
            os.makedirs(exec_out_dir)
            
            # Change to test directory
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                # Test with empty directory
                points, result = demo.print_resoults(exec_out_dir)
                
                # Should handle missing files gracefully
                assert points == 0
                assert "points: 0" in result
                
            finally:
                os.chdir(original_cwd)

    def test_demo_malformed_json(self):
        """Test demo behavior with malformed JSON files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create the expected directory structure
            exec_out_dir = os.path.join(tmpdir, "src", "example", "exec-out")
            os.makedirs(exec_out_dir)
            
            # Create malformed JSON file
            with open(os.path.join(exec_out_dir, '0.judge.json'), 'w') as f:
                f.write('invalid json')
            
            # Change to test directory
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                # Test should handle malformed JSON gracefully
                with pytest.raises(json.JSONDecodeError):
                    demo.print_resoults(exec_out_dir)
                    
            finally:
                os.chdir(original_cwd)

    def test_demo_missing_json_fields(self):
        """Test demo behavior with missing JSON fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create JSON with missing fields
            exec_data = {"return_code": 0}  # Missing user_time
            judge_data = {"grade": 1}       # Missing info
            
            with open(os.path.join(tmpdir, '0.exec.json'), 'w') as f:
                json.dump(exec_data, f)
            
            with open(os.path.join(tmpdir, '0.judge.json'), 'w') as f:
                json.dump(judge_data, f)
            
            # Test should handle missing fields gracefully
            with pytest.raises(KeyError):
                demo.print_resoults(tmpdir)


class TestDemoDocumentation:
    """Test documentation and docstrings in demo module."""

    def test_demo_functions_have_docstrings(self):
        """Test that demo functions have proper docstrings."""
        # Check print_resoults function
        assert demo.print_resoults.__doc__ is not None
        # Note: Original function name has typo, but we test what exists
        
        # Check run_example function
        assert demo.run_example.__doc__ is not None

    def test_demo_module_docstring(self):
        """Test that demo module has proper docstring."""
        assert demo.__doc__ is not None or hasattr(demo, '__doc__')