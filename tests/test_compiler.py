"""
Comprehensive unit tests for the cpp-compiler module.

This module contains detailed tests for the C++ compiler functionality,
including compilation success, failure cases, file handling, and error conditions.
"""

import pytest
import json
import os
import tempfile
import shutil
import subprocess
import sys
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

# Add the src directory to the path for importing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src/compilers/cpp-compiler'))

import main as compiler_main


class TestCppCompiler:
    """Test cases for the C++ compiler main functionality."""

    def setup_method(self):
        """Setup test environment variables."""
        self.original_env = {}
        env_vars = ['SRC', 'OUT', 'BIN']
        for var in env_vars:
            self.original_env[var] = os.environ.get(var)

    def teardown_method(self):
        """Restore original environment variables."""
        for var, value in self.original_env.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]

    def test_environment_variables_usage(self):
        """Test that compiler uses correct environment variables."""
        # Read the main.py file to verify environment variable usage
        main_script_path = os.path.join(os.path.dirname(__file__), '../src/compilers/cpp-compiler/main.py')
        
        with open(main_script_path, 'r') as f:
            content = f.read()
        
        # Check that all required environment variables are used
        assert 'SRC = os.getenv("SRC")' in content
        assert 'OUT = os.getenv("OUT")' in content
        assert 'BIN = os.getenv("BIN")' in content

    def test_temporary_directory_paths(self):
        """Test that compiler uses correct temporary directory paths."""
        main_script_path = os.path.join(os.path.dirname(__file__), '../src/compilers/cpp-compiler/main.py')
        
        with open(main_script_path, 'r') as f:
            content = f.read()
        
        # Check temporary directory definitions
        assert 'SRC_TMP = "/tmp/src"' in content
        assert 'BIN_TMP = "/tmp/bin"' in content
        assert 'OUT_TMP = "/tmp/out"' in content

    def test_output_file_paths(self):
        """Test that compiler defines correct output file paths."""
        main_script_path = os.path.join(os.path.dirname(__file__), '../src/compilers/cpp-compiler/main.py')
        
        with open(main_script_path, 'r') as f:
            content = f.read()
        
        # Check output file definitions
        assert 'DIAGNOSTIC_FILE = f"{OUT}/comp.txt"' in content
        assert 'OUT_FILE = f"{OUT}/comp.json"' in content


class TestCopySrcFiles:
    """Test cases for the copy_src_files function."""

    def test_copy_src_files_function_exists(self):
        """Test that copy_src_files function is defined."""
        assert hasattr(compiler_main, 'copy_src_files')
        assert callable(compiler_main.copy_src_files)

    @patch('os.makedirs')
    @patch('os.listdir')
    @patch('os.path.isfile')
    @patch('shutil.copy')
    def test_copy_src_files_basic_functionality(self, mock_copy, mock_isfile, mock_listdir, mock_makedirs):
        """Test basic functionality of copy_src_files."""
        # Setup mocks
        mock_listdir.return_value = ['main.cpp', 'helper.cpp', 'header.h', 'README.md']
        mock_isfile.side_effect = lambda x: x.endswith(('.cpp', '.h'))
        
        # Set environment
        os.environ['SRC'] = '/test/src'
        
        # Call function
        compiler_main.copy_src_files()
        
        # Verify makedirs was called
        mock_makedirs.assert_called_once_with('/tmp/src', exist_ok=True)
        
        # Verify copy was called for source files only
        expected_copies = [
            ('/test/src/main.cpp', '/tmp/src'),
            ('/test/src/helper.cpp', '/tmp/src'),
            ('/test/src/header.h', '/tmp/src')
        ]
        assert mock_copy.call_count == 3
        for expected_call in expected_copies:
            mock_copy.assert_any_call(*expected_call)

    def test_copy_src_files_with_real_files(self):
        """Test copy_src_files with real temporary files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            src_dir = os.path.join(tmpdir, 'src')
            os.makedirs(src_dir)
            
            # Create test files
            test_files = ['main.cpp', 'helper.cpp', 'header.h', 'README.md']
            for filename in test_files:
                filepath = os.path.join(src_dir, filename)
                with open(filepath, 'w') as f:
                    f.write(f'// Content of {filename}')
            
            # Set environment
            os.environ['SRC'] = src_dir
            
            # Call function
            compiler_main.copy_src_files()
            
            # Verify files were copied
            tmp_src = '/tmp/src'
            assert os.path.exists(tmp_src)
            
            copied_files = os.listdir(tmp_src)
            assert 'main.cpp' in copied_files
            assert 'helper.cpp' in copied_files
            assert 'header.h' in copied_files
            assert 'README.md' in copied_files
            
            # Verify content
            with open(os.path.join(tmp_src, 'main.cpp'), 'r') as f:
                assert f.read() == '// Content of main.cpp'

    def test_copy_src_files_empty_directory(self):
        """Test copy_src_files with empty source directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            src_dir = os.path.join(tmpdir, 'src')
            os.makedirs(src_dir)
            
            # Set environment
            os.environ['SRC'] = src_dir
            
            # Call function
            compiler_main.copy_src_files()
            
            # Verify tmp directory is created but empty
            tmp_src = '/tmp/src'
            assert os.path.exists(tmp_src)
            assert len(os.listdir(tmp_src)) == 0

    def test_copy_src_files_nonexistent_directory(self):
        """Test copy_src_files with nonexistent source directory."""
        os.environ['SRC'] = '/nonexistent/directory'
        
        with pytest.raises(FileNotFoundError):
            compiler_main.copy_src_files()


class TestCompile:
    """Test cases for the compile function."""

    def test_compile_function_exists(self):
        """Test that compile function is defined."""
        assert hasattr(compiler_main, 'compile')
        assert callable(compiler_main.compile)

    @patch('os.system')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_compile_success(self, mock_json_dump, mock_file, mock_system):
        """Test successful compilation."""
        # Mock successful compilation
        mock_system.return_value = 0
        
        # Set environment
        os.environ['OUT'] = '/test/out'
        os.environ['BIN'] = '/test/bin'
        
        # Call function
        compiler_main.compile()
        
        # Verify g++ command was called
        expected_command = 'g++ -Wextra -Wall -o /tmp/bin/program /tmp/src/*.cpp 2> /test/out/comp.txt'
        mock_system.assert_called_once_with(expected_command)
        
        # Verify metadata was written
        mock_file.assert_called_once_with('/test/out/comp.json', 'w')
        mock_json_dump.assert_called_once()
        
        # Check metadata content
        call_args = mock_json_dump.call_args[0]
        metadata = call_args[0]
        assert metadata['return_code'] == 0

    @patch('os.system')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_compile_failure(self, mock_json_dump, mock_file, mock_system):
        """Test compilation failure."""
        # Mock failed compilation
        mock_system.return_value = 256  # Non-zero return code
        
        # Set environment
        os.environ['OUT'] = '/test/out'
        os.environ['BIN'] = '/test/bin'
        
        # Call function
        compiler_main.compile()
        
        # Verify g++ command was called
        expected_command = 'g++ -Wextra -Wall -o /tmp/bin/program /tmp/src/*.cpp 2> /test/out/comp.txt'
        mock_system.assert_called_once_with(expected_command)
        
        # Verify metadata was written with error
        mock_json_dump.assert_called_once()
        call_args = mock_json_dump.call_args[0]
        metadata = call_args[0]
        assert metadata['return_code'] == 256

    def test_compile_compiler_flags(self):
        """Test that compiler uses correct flags."""
        main_script_path = os.path.join(os.path.dirname(__file__), '../src/compilers/cpp-compiler/main.py')
        
        with open(main_script_path, 'r') as f:
            content = f.read()
        
        # Check compiler flags
        assert '-Wextra' in content
        assert '-Wall' in content
        assert 'g++' in content

    def test_compile_output_redirection(self):
        """Test that compiler redirects errors correctly."""
        main_script_path = os.path.join(os.path.dirname(__file__), '../src/compilers/cpp-compiler/main.py')
        
        with open(main_script_path, 'r') as f:
            content = f.read()
        
        # Check error redirection
        assert '2> {DIAGNOSTIC_FILE}' in content


class TestCopyOutFiles:
    """Test cases for the copy_out_files function."""

    def test_copy_out_files_function_exists(self):
        """Test that copy_out_files function is defined."""
        assert hasattr(compiler_main, 'copy_out_files')
        assert callable(compiler_main.copy_out_files)

    @patch('os.listdir')
    @patch('os.path.isfile')
    @patch('shutil.copy')
    def test_copy_out_files_basic_functionality(self, mock_copy, mock_isfile, mock_listdir):
        """Test basic functionality of copy_out_files."""
        # Setup mocks
        mock_listdir.side_effect = lambda x: {
            '/tmp/out': ['comp.json', 'debug.log'],
            '/tmp/bin': ['program', 'debug_info']
        }[x]
        mock_isfile.return_value = True
        
        # Set environment
        os.environ['OUT'] = '/test/out'
        os.environ['BIN'] = '/test/bin'
        
        # Call function
        compiler_main.copy_out_files()
        
        # Verify all files were copied
        expected_copies = [
            ('/tmp/out/comp.json', '/test/out'),
            ('/tmp/out/debug.log', '/test/out'),
            ('/tmp/bin/program', '/test/bin'),
            ('/tmp/bin/debug_info', '/test/bin')
        ]
        assert mock_copy.call_count == 4
        for expected_call in expected_copies:
            mock_copy.assert_any_call(*expected_call)

    def test_copy_out_files_with_real_files(self):
        """Test copy_out_files with real temporary files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = os.path.join(tmpdir, 'out')
            bin_dir = os.path.join(tmpdir, 'bin')
            os.makedirs(out_dir)
            os.makedirs(bin_dir)
            
            # Create temporary directories and files
            os.makedirs('/tmp/out', exist_ok=True)
            os.makedirs('/tmp/bin', exist_ok=True)
            
            # Create test files in temporary directories
            with open('/tmp/out/comp.json', 'w') as f:
                f.write('{"return_code": 0}')
            with open('/tmp/bin/program', 'w') as f:
                f.write('#!/bin/bash\necho "Hello World"')
            
            # Set environment
            os.environ['OUT'] = out_dir
            os.environ['BIN'] = bin_dir
            
            # Call function
            compiler_main.copy_out_files()
            
            # Verify files were copied
            assert os.path.exists(os.path.join(out_dir, 'comp.json'))
            assert os.path.exists(os.path.join(bin_dir, 'program'))
            
            # Verify content
            with open(os.path.join(out_dir, 'comp.json'), 'r') as f:
                assert f.read() == '{"return_code": 0}'

    def test_copy_out_files_empty_directories(self):
        """Test copy_out_files with empty temporary directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = os.path.join(tmpdir, 'out')
            bin_dir = os.path.join(tmpdir, 'bin')
            os.makedirs(out_dir)
            os.makedirs(bin_dir)
            
            # Create empty temporary directories
            os.makedirs('/tmp/out', exist_ok=True)
            os.makedirs('/tmp/bin', exist_ok=True)
            
            # Set environment
            os.environ['OUT'] = out_dir
            os.environ['BIN'] = bin_dir
            
            # Call function (should not raise errors)
            compiler_main.copy_out_files()
            
            # Verify no files were copied
            assert len(os.listdir(out_dir)) == 0
            assert len(os.listdir(bin_dir)) == 0


class TestMainFunction:
    """Test cases for the main function and overall workflow."""

    def test_main_function_exists(self):
        """Test that main function is defined."""
        main_script_path = os.path.join(os.path.dirname(__file__), '../src/compilers/cpp-compiler/main.py')
        
        with open(main_script_path, 'r') as f:
            content = f.read()
        
        # Check main function structure
        assert 'if __name__ == "__main__":' in content
        assert 'os.umask(0)' in content
        assert 'copy_src_files()' in content
        assert 'compile()' in content
        assert 'copy_out_files()' in content

    @patch('compiler_main.copy_src_files')
    @patch('compiler_main.compile')
    @patch('compiler_main.copy_out_files')
    @patch('os.umask')
    def test_main_execution_order(self, mock_umask, mock_copy_out, mock_compile, mock_copy_src):
        """Test that main function executes steps in correct order."""
        # Import and reload to test main execution
        import importlib
        importlib.reload(compiler_main)
        
        # Since we can't easily test the main block, we'll verify the function calls
        # would be made in the correct order by checking the file structure
        main_script_path = os.path.join(os.path.dirname(__file__), '../src/compilers/cpp-compiler/main.py')
        
        with open(main_script_path, 'r') as f:
            content = f.read()
        
        # Check that functions are called in the correct order
        lines = content.split('\n')
        main_block_started = False
        function_calls = []
        
        for line in lines:
            if 'if __name__ == "__main__":' in line:
                main_block_started = True
            elif main_block_started and line.strip():
                if 'copy_src_files()' in line:
                    function_calls.append('copy_src_files')
                elif 'compile()' in line:
                    function_calls.append('compile')
                elif 'copy_out_files()' in line:
                    function_calls.append('copy_out_files')
        
        # Verify correct order
        expected_order = ['copy_src_files', 'compile', 'copy_out_files']
        assert function_calls == expected_order

    def test_umask_setting(self):
        """Test that umask is set correctly."""
        main_script_path = os.path.join(os.path.dirname(__file__), '../src/compilers/cpp-compiler/main.py')
        
        with open(main_script_path, 'r') as f:
            content = f.read()
        
        # Check umask setting
        assert 'os.umask(0)' in content


class TestErrorHandling:
    """Test cases for error handling and edge cases."""

    def test_missing_environment_variables(self):
        """Test behavior when environment variables are missing."""
        # Clear environment variables
        for var in ['SRC', 'OUT', 'BIN']:
            if var in os.environ:
                del os.environ[var]
        
        # Test that functions handle missing environment variables
        with pytest.raises(TypeError):
            compiler_main.copy_src_files()

    def test_compile_with_missing_source_files(self):
        """Test compilation with missing source files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create empty directory
            os.makedirs('/tmp/src', exist_ok=True)
            
            # Set environment
            os.environ['OUT'] = tmpdir
            os.environ['BIN'] = tmpdir
            
            # Call compile (should fail but not crash)
            compiler_main.compile()
            
            # Verify metadata file was created
            comp_json_path = os.path.join(tmpdir, 'comp.json')
            assert os.path.exists(comp_json_path)
            
            with open(comp_json_path, 'r') as f:
                metadata = json.load(f)
            
            # Should have non-zero return code
            assert metadata['return_code'] != 0

    def test_compile_with_syntax_errors(self):
        """Test compilation with syntax errors in source files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directory with invalid C++ file
            src_tmp = '/tmp/src'
            os.makedirs(src_tmp, exist_ok=True)
            
            with open(os.path.join(src_tmp, 'bad.cpp'), 'w') as f:
                f.write('this is not valid C++ code')
            
            # Set environment
            os.environ['OUT'] = tmpdir
            os.environ['BIN'] = tmpdir
            
            # Call compile (should fail)
            compiler_main.compile()
            
            # Verify metadata file was created
            comp_json_path = os.path.join(tmpdir, 'comp.json')
            assert os.path.exists(comp_json_path)
            
            with open(comp_json_path, 'r') as f:
                metadata = json.load(f)
            
            # Should have non-zero return code
            assert metadata['return_code'] != 0
            
            # Verify diagnostic file was created
            diag_file_path = os.path.join(tmpdir, 'comp.txt')
            assert os.path.exists(diag_file_path)


class TestIntegration:
    """Integration tests for the complete compiler workflow."""

    def test_successful_compilation_workflow(self):
        """Test complete successful compilation workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source directory with valid C++ files
            src_dir = os.path.join(tmpdir, 'src')
            out_dir = os.path.join(tmpdir, 'out')
            bin_dir = os.path.join(tmpdir, 'bin')
            
            os.makedirs(src_dir)
            os.makedirs(out_dir)
            os.makedirs(bin_dir)
            
            # Create simple valid C++ program
            with open(os.path.join(src_dir, 'main.cpp'), 'w') as f:
                f.write('#include <iostream>\nint main() { std::cout << "Hello World" << std::endl; return 0; }')
            
            # Set environment
            os.environ['SRC'] = src_dir
            os.environ['OUT'] = out_dir
            os.environ['BIN'] = bin_dir
            
            # Run the complete workflow
            compiler_main.copy_src_files()
            compiler_main.compile()
            compiler_main.copy_out_files()
            
            # Verify all steps completed successfully
            assert os.path.exists(os.path.join(out_dir, 'comp.json'))
            
            with open(os.path.join(out_dir, 'comp.json'), 'r') as f:
                metadata = json.load(f)
            
            # Should have successful compilation
            assert metadata['return_code'] == 0
            
            # Verify binary was created
            program_path = os.path.join(bin_dir, 'program')
            assert os.path.exists(program_path)
            
            # Verify program is executable
            assert os.access(program_path, os.X_OK)

    def test_compilation_failure_workflow(self):
        """Test complete compilation failure workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source directory with invalid C++ files
            src_dir = os.path.join(tmpdir, 'src')
            out_dir = os.path.join(tmpdir, 'out')
            bin_dir = os.path.join(tmpdir, 'bin')
            
            os.makedirs(src_dir)
            os.makedirs(out_dir)
            os.makedirs(bin_dir)
            
            # Create invalid C++ program
            with open(os.path.join(src_dir, 'main.cpp'), 'w') as f:
                f.write('invalid C++ code that will not compile')
            
            # Set environment
            os.environ['SRC'] = src_dir
            os.environ['OUT'] = out_dir
            os.environ['BIN'] = bin_dir
            
            # Run the complete workflow
            compiler_main.copy_src_files()
            compiler_main.compile()
            compiler_main.copy_out_files()
            
            # Verify compilation failed
            assert os.path.exists(os.path.join(out_dir, 'comp.json'))
            
            with open(os.path.join(out_dir, 'comp.json'), 'r') as f:
                metadata = json.load(f)
            
            # Should have failed compilation
            assert metadata['return_code'] != 0
            
            # Verify diagnostic file was created
            assert os.path.exists(os.path.join(out_dir, 'comp.txt'))
            
            # Verify no binary was created
            program_path = os.path.join(bin_dir, 'program')
            assert not os.path.exists(program_path)

    def test_multiple_source_files_compilation(self):
        """Test compilation with multiple source files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source directory with multiple C++ files
            src_dir = os.path.join(tmpdir, 'src')
            out_dir = os.path.join(tmpdir, 'out')
            bin_dir = os.path.join(tmpdir, 'bin')
            
            os.makedirs(src_dir)
            os.makedirs(out_dir)
            os.makedirs(bin_dir)
            
            # Create header file
            with open(os.path.join(src_dir, 'math.h'), 'w') as f:
                f.write('int add(int a, int b);')
            
            # Create implementation file
            with open(os.path.join(src_dir, 'math.cpp'), 'w') as f:
                f.write('#include "math.h"\nint add(int a, int b) { return a + b; }')
            
            # Create main file
            with open(os.path.join(src_dir, 'main.cpp'), 'w') as f:
                f.write('#include <iostream>\n#include "math.h"\nint main() { std::cout << add(1, 2) << std::endl; return 0; }')
            
            # Set environment
            os.environ['SRC'] = src_dir
            os.environ['OUT'] = out_dir
            os.environ['BIN'] = bin_dir
            
            # Run the complete workflow
            compiler_main.copy_src_files()
            compiler_main.compile()
            compiler_main.copy_out_files()
            
            # Verify compilation succeeded
            assert os.path.exists(os.path.join(out_dir, 'comp.json'))
            
            with open(os.path.join(out_dir, 'comp.json'), 'r') as f:
                metadata = json.load(f)
            
            # Should have successful compilation
            assert metadata['return_code'] == 0
            
            # Verify binary was created
            program_path = os.path.join(bin_dir, 'program')
            assert os.path.exists(program_path)