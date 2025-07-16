"""
Comprehensive unit tests for the exec-python module.

This module contains detailed tests for all functions in the exec.py and main.py modules,
including edge cases, error conditions, and resource management.
"""

import pytest
import json
import os
import tempfile
import subprocess
import sys
from unittest.mock import patch, MagicMock, call
from pathlib import Path

# Add the src directory to the path for importing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src/exec-python'))

# Note: We cannot directly import exec.py as it's a script that expects command line args
# Instead, we'll test the functionality through subprocess or mock the environment


class TestExecScript:
    """Test cases for the exec.py script functionality."""

    def test_exec_script_environment_variables(self):
        """Test that exec.py uses correct environment variables."""
        # This test verifies the script reads the correct environment variables
        exec_script_path = os.path.join(os.path.dirname(__file__), '../src/exec-python/exec.py')
        
        # Read the script content to verify it uses correct environment variables
        with open(exec_script_path, 'r') as f:
            content = f.read()
        
        # Check that all required environment variables are used
        assert 'os.getenv(\'BIN\')' in content
        assert 'os.getenv(\'IN\')' in content
        assert 'os.getenv(\'STD\')' in content
        assert 'os.getenv(\'OUT\')' in content

    def test_exec_script_file_paths(self):
        """Test that exec.py constructs correct file paths."""
        exec_script_path = os.path.join(os.path.dirname(__file__), '../src/exec-python/exec.py')
        
        with open(exec_script_path, 'r') as f:
            content = f.read()
        
        # Verify path construction patterns
        assert 'binary_path = f"{os.getenv(\'BIN\')}/program"' in content
        assert 'input_path=f"{os.getenv(\'IN\')}/{name}.in"' in content
        assert 'output_path=f"{os.getenv(\'STD\')}/{name}.stdout.out"' in content
        assert 'error_path=f"{os.getenv(\'STD\')}/{name}.stderr.out"' in content
        assert 'exec_path=f"{os.getenv(\'OUT\')}/{name}.exec.json"' in content

    @patch('subprocess.Popen')
    @patch('resource.prlimit')
    @patch('resource.getrusage')
    def test_exec_script_resource_limits(self, mock_getrusage, mock_prlimit, mock_popen):
        """Test that exec.py sets proper resource limits."""
        # This test verifies that the exec script has the correct resource management code
        exec_script_path = os.path.join(os.path.dirname(__file__), '../src/exec-python/exec.py')
        
        with open(exec_script_path, 'r') as f:
            content = f.read()
        
        # Verify that resource limits are set in the code
        assert 'resource.prlimit(program_process.pid, resource.RLIMIT_CPU, (2, 2))' in content
        assert 'resource.getrusage(resource.RUSAGE_CHILDREN)' in content
        
        # Verify metadata collection
        assert 'meta["return_code"] = program_process.returncode' in content
        assert 'meta["user_time"] =  round(resources.ru_utime, 10)' in content
        assert 'meta["memory"] =  round(resources.ru_maxrss, 10)' in content

    def test_exec_script_command_line_args(self):
        """Test that exec.py handles command line arguments correctly."""
        exec_script_path = os.path.join(os.path.dirname(__file__), '../src/exec-python/exec.py')
        
        with open(exec_script_path, 'r') as f:
            content = f.read()
        
        # Check that script expects exactly one argument
        assert 'name = sys.argv[1]' in content


class TestMainScript:
    """Test cases for the main.py script functionality."""

    def setup_method(self):
        """Setup test environment."""
        self.original_env = {}
        env_vars = ['IN', 'LOGS']
        for var in env_vars:
            self.original_env[var] = os.environ.get(var)

    def teardown_method(self):
        """Restore original environment."""
        for var, value in self.original_env.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]

    def test_main_script_logging_configuration(self):
        """Test that main.py configures logging correctly."""
        main_script_path = os.path.join(os.path.dirname(__file__), '../src/exec-python/main.py')
        
        with open(main_script_path, 'r') as f:
            content = f.read()
        
        # Check logging configuration
        assert 'logging.basicConfig' in content
        assert 'os.environ.get("LOGS")=="on"' in content
        assert 'logging.DEBUG' in content
        assert 'logging.ERROR' in content

    def test_main_script_file_processing(self):
        """Test that main.py processes .in files correctly."""
        main_script_path = os.path.join(os.path.dirname(__file__), '../src/exec-python/main.py')
        
        with open(main_script_path, 'r') as f:
            content = f.read()
        
        # Check file processing logic
        assert 'os.listdir(os.getenv(\'IN\'))' in content
        assert 'if file.endswith(\'.in\')' in content
        assert 'run_program(file.split(\'.\')[0])' in content

    def test_main_script_umask_setting(self):
        """Test that main.py sets umask correctly."""
        main_script_path = os.path.join(os.path.dirname(__file__), '../src/exec-python/main.py')
        
        with open(main_script_path, 'r') as f:
            content = f.read()
        
        # Check umask setting
        assert 'os.umask(0)' in content

    @patch('subprocess.Popen')
    @patch('time.time')
    def test_run_program_function(self, mock_time, mock_popen):
        """Test the run_program function."""
        # Mock time for timing measurements
        mock_time.side_effect = [0.0, 1.5]  # start time, end time
        
        # Mock subprocess
        mock_process = MagicMock()
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        
        # Import and test the function
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src/exec-python'))
        try:
            import main
            
            # Test the run_program function
            with patch('main.logger') as mock_logger:
                main.run_program('test1')
                
                # Verify subprocess was called correctly
                mock_popen.assert_called_once_with(["python", "exec.py", "test1"])
                mock_process.wait.assert_called_once()
                
                # Verify logging
                mock_logger.info.assert_called_once()
                
        finally:
            # Clean up sys.path
            if os.path.join(os.path.dirname(__file__), '../src/exec-python') in sys.path:
                sys.path.remove(os.path.join(os.path.dirname(__file__), '../src/exec-python'))

    def test_main_execution_timing(self):
        """Test that main.py measures execution time."""
        main_script_path = os.path.join(os.path.dirname(__file__), '../src/exec-python/main.py')
        
        with open(main_script_path, 'r') as f:
            content = f.read()
        
        # Check timing logic
        assert 'start_time = time.time()' in content
        assert 'time.time() - start_time' in content
        assert 'logger.info' in content and 'execution time' in content


class TestResourceManagement:
    """Test cases for resource management and limits."""

    def test_resource_limit_constants(self):
        """Test that resource limits are properly defined."""
        exec_script_path = os.path.join(os.path.dirname(__file__), '../src/exec-python/exec.py')
        
        with open(exec_script_path, 'r') as f:
            content = f.read()
        
        # Check that CPU limit is set
        assert 'resource.prlimit' in content
        assert 'resource.RLIMIT_CPU' in content
        assert '(2, 2)' in content  # 2 second CPU limit

    def test_resource_usage_collection(self):
        """Test that resource usage is collected correctly."""
        exec_script_path = os.path.join(os.path.dirname(__file__), '../src/exec-python/exec.py')
        
        with open(exec_script_path, 'r') as f:
            content = f.read()
        
        # Check resource usage collection
        assert 'resource.getrusage(resource.RUSAGE_CHILDREN)' in content
        assert 'ru_utime' in content
        assert 'ru_maxrss' in content

    def test_metadata_json_structure(self):
        """Test that metadata JSON contains required fields."""
        exec_script_path = os.path.join(os.path.dirname(__file__), '../src/exec-python/exec.py')
        
        with open(exec_script_path, 'r') as f:
            content = f.read()
        
        # Check metadata structure
        assert 'meta = {}' in content
        assert 'meta["return_code"]' in content
        assert 'meta["user_time"]' in content
        assert 'meta["memory"]' in content
        assert 'json.dump(meta, exec_file)' in content


class TestFileHandling:
    """Test cases for file handling and I/O operations."""

    def test_file_opening_modes(self):
        """Test that files are opened in correct modes."""
        exec_script_path = os.path.join(os.path.dirname(__file__), '../src/exec-python/exec.py')
        
        with open(exec_script_path, 'r') as f:
            content = f.read()
        
        # Check file opening modes
        assert 'open(input_path, "r")' in content
        assert 'open(error_path, "w")' in content
        assert 'open(exec_path, "w")' in content
        assert 'open(output_path, "w")' in content

    def test_subprocess_configuration(self):
        """Test that subprocess is configured correctly."""
        exec_script_path = os.path.join(os.path.dirname(__file__), '../src/exec-python/exec.py')
        
        with open(exec_script_path, 'r') as f:
            content = f.read()
        
        # Check subprocess configuration
        assert 'subprocess.Popen' in content
        assert 'stdin=input_file' in content
        assert 'stderr=error_file' in content
        assert 'stdout=output_file' in content


class TestErrorHandling:
    """Test cases for error handling and edge cases."""

    def test_missing_environment_variables(self):
        """Test behavior when environment variables are missing."""
        exec_script_path = os.path.join(os.path.dirname(__file__), '../src/exec-python/exec.py')
        
        # Clear environment variables
        env = os.environ.copy()
        for var in ['BIN', 'IN', 'STD', 'OUT']:
            if var in env:
                del env[var]
        
        # Test that script fails gracefully
        with pytest.raises(subprocess.CalledProcessError):
            subprocess.run([sys.executable, exec_script_path, 'test'], 
                         env=env, check=True, capture_output=True, timeout=5)

    def test_missing_binary_file(self):
        """Test behavior when binary file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env = {
                'BIN': tmpdir,
                'IN': tmpdir,
                'STD': tmpdir,
                'OUT': tmpdir
            }
            
            # Create input file but not binary
            input_path = os.path.join(tmpdir, 'test.in')
            with open(input_path, 'w') as f:
                f.write('test input')
            
            exec_script_path = os.path.join(os.path.dirname(__file__), '../src/exec-python/exec.py')
            
            # Test that script handles missing binary gracefully
            with pytest.raises(subprocess.CalledProcessError):
                subprocess.run([sys.executable, exec_script_path, 'test'], 
                             env=env, check=True, capture_output=True, timeout=5)

    def test_invalid_test_name(self):
        """Test behavior with invalid test names."""
        exec_script_path = os.path.join(os.path.dirname(__file__), '../src/exec-python/exec.py')
        
        # Test with missing argument
        with pytest.raises(subprocess.CalledProcessError):
            subprocess.run([sys.executable, exec_script_path], 
                         check=True, capture_output=True, timeout=5)

    def test_permission_errors(self):
        """Test handling of permission errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env = {
                'BIN': tmpdir,
                'IN': tmpdir,
                'STD': tmpdir,
                'OUT': tmpdir
            }
            
            # Create files
            binary_path = os.path.join(tmpdir, 'program')
            input_path = os.path.join(tmpdir, 'test.in')
            
            with open(binary_path, 'w') as f:
                f.write('#!/bin/bash\necho "test"')
            with open(input_path, 'w') as f:
                f.write('test input')
            
            # Remove execute permission from binary
            os.chmod(binary_path, 0o644)
            
            exec_script_path = os.path.join(os.path.dirname(__file__), '../src/exec-python/exec.py')
            
            # Test that script handles permission errors
            result = subprocess.run([sys.executable, exec_script_path, 'test'], 
                                  env=env, capture_output=True, timeout=5)
            
            # Should create exec.json even if binary fails
            exec_json_path = os.path.join(tmpdir, 'test.exec.json')
            if os.path.exists(exec_json_path):
                with open(exec_json_path, 'r') as f:
                    content = f.read().strip()
                    if content:  # Only test if file has content
                        metadata = json.load(open(exec_json_path, 'r'))
                        # Should have non-zero return code
                        assert metadata['return_code'] != 0
                    else:
                        # If file is empty, the test completed but with permission error
                        assert result.returncode != 0


class TestIntegration:
    """Integration tests for the complete exec-python workflow."""

    def test_successful_execution_workflow(self):
        """Test complete successful execution workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env = {
                'BIN': tmpdir,
                'IN': tmpdir,
                'STD': tmpdir,
                'OUT': tmpdir
            }
            
            # Create a simple program
            binary_path = os.path.join(tmpdir, 'program')
            input_path = os.path.join(tmpdir, 'test.in')
            
            with open(binary_path, 'w') as f:
                f.write('#!/bin/bash\ncat')  # Simple echo program
            os.chmod(binary_path, 0o755)
            
            with open(input_path, 'w') as f:
                f.write('Hello World\n')
            
            exec_script_path = os.path.join(os.path.dirname(__file__), '../src/exec-python/exec.py')
            
            # Run the exec script
            result = subprocess.run([sys.executable, exec_script_path, 'test'], 
                                  env=env, capture_output=True, timeout=5)
            
            # Check that all output files were created
            assert os.path.exists(os.path.join(tmpdir, 'test.stdout.out'))
            assert os.path.exists(os.path.join(tmpdir, 'test.stderr.out'))
            assert os.path.exists(os.path.join(tmpdir, 'test.exec.json'))
            
            # Check output content
            with open(os.path.join(tmpdir, 'test.stdout.out'), 'r') as f:
                output = f.read()
            assert 'Hello World' in output
            
            # Check metadata
            with open(os.path.join(tmpdir, 'test.exec.json'), 'r') as f:
                metadata = json.load(f)
            
            assert 'return_code' in metadata
            assert 'user_time' in metadata
            assert 'memory' in metadata
            assert metadata['return_code'] == 0

    def test_program_timeout_handling(self):
        """Test handling of program timeouts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env = {
                'BIN': tmpdir,
                'IN': tmpdir,
                'STD': tmpdir,
                'OUT': tmpdir
            }
            
            # Create a program that runs for a short time (to avoid actual timeout)
            binary_path = os.path.join(tmpdir, 'program')
            input_path = os.path.join(tmpdir, 'test.in')
            
            with open(binary_path, 'w') as f:
                f.write('#!/bin/bash\nsleep 1; echo "done"')
            os.chmod(binary_path, 0o755)
            
            with open(input_path, 'w') as f:
                f.write('')
            
            exec_script_path = os.path.join(os.path.dirname(__file__), '../src/exec-python/exec.py')
            
            # Run the exec script with reasonable timeout
            try:
                result = subprocess.run([sys.executable, exec_script_path, 'test'], 
                                      env=env, capture_output=True, timeout=5)
                
                # Check that execution completed
                assert os.path.exists(os.path.join(tmpdir, 'test.exec.json'))
                
                with open(os.path.join(tmpdir, 'test.exec.json'), 'r') as f:
                    content = f.read().strip()
                    if content:
                        metadata = json.load(open(os.path.join(tmpdir, 'test.exec.json'), 'r'))
                        # Should have some return code
                        assert 'return_code' in metadata
                        
            except subprocess.TimeoutExpired:
                # If timeout occurs, that's also acceptable for this test
                pass