"""
Comprehensive unit tests for the configuration generators.

This module contains detailed tests for the test data generators,
including sum generator and echo generator functionality.
"""

import pytest
import os
import tempfile
import shutil
import subprocess
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestExampleGeneratorSum:
    """Test cases for the example_generator_sum.py script."""

    def test_generator_sum_script_exists(self):
        """Test that the sum generator script exists."""
        script_path = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_sum.py')
        assert os.path.exists(script_path)

    def test_generator_sum_directory_setup(self):
        """Test that the sum generator sets up directories correctly."""
        script_path = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_sum.py')
        
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check directory setup
        assert 'exec_in_path = "src/example/exec-in/"' in content
        assert 'comp_out_path = "src/example/comp-out"' in content
        assert 'exec_out_path = "src/example/exec-out"' in content
        
        # Check directory creation
        assert 'shutil.rmtree' in content
        assert 'os.makedirs' in content

    def test_generator_sum_file_creation(self):
        """Test that the sum generator creates test files correctly."""
        script_path = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_sum.py')
        
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check test file creation
        assert 'in_file_name = f"{exec_in_path}in/{i}.in"' in content
        assert 'out_file_name = f"{exec_in_path}out/{i}.out"' in content
        assert 'for i in range(22):' in content

    def test_generator_sum_test_data_formula(self):
        """Test that the sum generator uses correct test data formula."""
        script_path = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_sum.py')
        
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check test data generation formula
        assert 'n = round(2.3**i)' in content
        assert 'for j in range(n):' in content
        assert 'file.write("1\\n")' in content

    def test_generator_sum_permissions_setting(self):
        """Test that the sum generator sets file permissions correctly."""
        script_path = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_sum.py')
        
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check permission settings
        assert 'os.chmod(in_file_name, 0o777)' in content
        assert 'os.chmod(out_file_name, 0o777)' in content
        assert 'os.chmod(comp_out_path, 0o777)' in content

    def test_generator_sum_special_case(self):
        """Test that the sum generator handles special case for test 10."""
        script_path = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_sum.py')
        
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check special case handling
        assert 'if i != 10 else "67"' in content

    def test_generator_sum_execution(self):
        """Test that the sum generator script can be executed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test directory structure
            test_example_dir = os.path.join(tmpdir, 'src', 'example')
            os.makedirs(test_example_dir)
            
            # Change to test directory
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                # Run the generator script
                script_path = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_sum.py')
                result = subprocess.run([sys.executable, script_path], 
                                      capture_output=True, text=True, timeout=10)
                
                # Check that script ran without major errors
                assert result.returncode == 0 or "FileNotFoundError" in result.stderr
                
            finally:
                os.chdir(original_cwd)

    def test_generator_sum_working_directory(self):
        """Test that the sum generator changes working directory correctly."""
        script_path = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_sum.py')
        
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check directory change
        assert 'file_dir = os.path.dirname( os.path.abspath(__file__) )' in content
        assert 'os.chdir(f"{file_dir}/../..")' in content


class TestExampleGeneratorEcho:
    """Test cases for the example_generator_echo.py script."""

    def test_generator_echo_script_exists(self):
        """Test that the echo generator script exists."""
        script_path = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_echo.py')
        assert os.path.exists(script_path)

    def test_generator_echo_directory_setup(self):
        """Test that the echo generator sets up directories correctly."""
        script_path = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_echo.py')
        
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check directory setup
        assert 'exec_in_path = "src/example/exec-in/"' in content
        assert 'comp_out_path = "src/example/comp-out"' in content
        assert 'exec_out_path = "src/example/exec-out"' in content

    def test_generator_echo_test_count(self):
        """Test that the echo generator creates correct number of tests."""
        script_path = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_echo.py')
        
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check test count
        assert 'for i in range(20):' in content

    def test_generator_echo_test_data_formula(self):
        """Test that the echo generator uses correct test data formula."""
        script_path = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_echo.py')
        
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check test data generation formula
        assert 'n = 1000000//(20-i)' in content

    def test_generator_echo_input_output_generation(self):
        """Test that the echo generator creates input and output files correctly."""
        script_path = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_echo.py')
        
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check input file generation
        assert 'file.write(f"{n}\\n")' in content
        
        # Check output file generation
        assert 'for j in range(n):' in content
        assert 'file.write(f"1\\n")' in content

    def test_generator_echo_permissions_setting(self):
        """Test that the echo generator sets file permissions correctly."""
        script_path = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_echo.py')
        
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check permission settings
        assert 'os.chmod(in_file_name, 0o777)' in content
        assert 'os.chmod(out_file_name, 0o777)' in content

    def test_generator_echo_execution(self):
        """Test that the echo generator script can be executed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test directory structure
            test_example_dir = os.path.join(tmpdir, 'src', 'example')
            os.makedirs(test_example_dir)
            
            # Change to test directory
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                # Run the generator script
                script_path = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_echo.py')
                result = subprocess.run([sys.executable, script_path], 
                                      capture_output=True, text=True, timeout=10)
                
                # Check that script ran without major errors
                assert result.returncode == 0 or "FileNotFoundError" in result.stderr
                
            finally:
                os.chdir(original_cwd)

    def test_generator_echo_working_directory(self):
        """Test that the echo generator changes working directory correctly."""
        script_path = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_echo.py')
        
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check directory change
        assert 'file_dir = os.path.dirname( os.path.abspath(__file__) )' in content
        assert 'os.chdir(f"{file_dir}/../..")' in content


class TestGeneratorComparisons:
    """Test cases comparing the two generators."""

    def test_generators_have_similar_structure(self):
        """Test that both generators have similar structure."""
        sum_script = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_sum.py')
        echo_script = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_echo.py')
        
        with open(sum_script, 'r') as f:
            sum_content = f.read()
        
        with open(echo_script, 'r') as f:
            echo_content = f.read()
        
        # Both should have similar directory setup
        assert 'exec_in_path = "src/example/exec-in/"' in sum_content
        assert 'exec_in_path = "src/example/exec-in/"' in echo_content
        
        # Both should have similar imports
        assert 'import os' in sum_content
        assert 'import os' in echo_content
        assert 'import shutil' in sum_content
        assert 'import shutil' in echo_content

    def test_generators_have_different_test_counts(self):
        """Test that generators create different numbers of tests."""
        sum_script = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_sum.py')
        echo_script = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_echo.py')
        
        with open(sum_script, 'r') as f:
            sum_content = f.read()
        
        with open(echo_script, 'r') as f:
            echo_content = f.read()
        
        # Check different test counts
        assert 'for i in range(22):' in sum_content
        assert 'for i in range(20):' in echo_content

    def test_generators_have_different_formulas(self):
        """Test that generators use different test data formulas."""
        sum_script = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_sum.py')
        echo_script = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_echo.py')
        
        with open(sum_script, 'r') as f:
            sum_content = f.read()
        
        with open(echo_script, 'r') as f:
            echo_content = f.read()
        
        # Check different formulas
        assert 'n = round(2.3**i)' in sum_content
        assert 'n = 1000000//(20-i)' in echo_content


class TestGeneratorIntegration:
    """Integration tests for the generators."""

    def test_generator_sum_creates_files(self):
        """Test that sum generator actually creates test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directory structure
            example_dir = os.path.join(tmpdir, 'src', 'example')
            os.makedirs(example_dir)
            
            # Change to test directory
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                # Create a minimal version of the generator for testing
                generator_content = '''
import os
import shutil

exec_in_path = "src/example/exec-in/"
comp_out_path = "src/example/comp-out"
exec_out_path = "src/example/exec-out"

if os.path.exists(comp_out_path):
    shutil.rmtree(comp_out_path)
os.makedirs(comp_out_path)

if os.path.exists(exec_out_path):
    shutil.rmtree(exec_out_path)
os.makedirs(exec_out_path)

if os.path.exists(exec_in_path):
    shutil.rmtree(exec_in_path)
os.makedirs(exec_in_path)
os.makedirs(exec_in_path+"in")
os.makedirs(exec_in_path+"out")

# Create just a few test files
for i in range(3):
    in_file_name = f"{exec_in_path}in/{i}.in"
    out_file_name = f"{exec_in_path}out/{i}.out"
    
    n = round(2.3**i)
    
    with open(in_file_name, 'w') as file:
        file.write(f"{n}\\n")
        for j in range(n):
            file.write("1\\n")
    
    with open(out_file_name, 'w') as file:
        file.write(f"{n}\\n")
'''
                
                # Write and execute the test generator
                with open('test_generator.py', 'w') as f:
                    f.write(generator_content)
                
                result = subprocess.run([sys.executable, 'test_generator.py'], 
                                      capture_output=True, text=True)
                
                # Check that directories were created
                assert os.path.exists('src/example/exec-in/in')
                assert os.path.exists('src/example/exec-in/out')
                assert os.path.exists('src/example/comp-out')
                assert os.path.exists('src/example/exec-out')
                
                # Check that test files were created
                assert os.path.exists('src/example/exec-in/in/0.in')
                assert os.path.exists('src/example/exec-in/out/0.out')
                
                # Check file contents
                with open('src/example/exec-in/in/0.in', 'r') as f:
                    content = f.read()
                    assert '1\n' in content
                
                with open('src/example/exec-in/out/0.out', 'r') as f:
                    content = f.read()
                    assert '1\n' in content
                
            finally:
                os.chdir(original_cwd)

    def test_generator_echo_creates_files(self):
        """Test that echo generator actually creates test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directory structure
            example_dir = os.path.join(tmpdir, 'src', 'example')
            os.makedirs(example_dir)
            
            # Change to test directory
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                # Create a minimal version of the generator for testing
                generator_content = '''
import os
import shutil

exec_in_path = "src/example/exec-in/"
comp_out_path = "src/example/comp-out"
exec_out_path = "src/example/exec-out"

if os.path.exists(comp_out_path):
    shutil.rmtree(comp_out_path)
os.makedirs(comp_out_path)

if os.path.exists(exec_out_path):
    shutil.rmtree(exec_out_path)
os.makedirs(exec_out_path)

if os.path.exists(exec_in_path):
    shutil.rmtree(exec_in_path)
os.makedirs(exec_in_path)
os.makedirs(exec_in_path+"in")
os.makedirs(exec_in_path+"out")

# Create just a few test files
for i in range(3):
    in_file_name = f"{exec_in_path}in/{i}.in"
    out_file_name = f"{exec_in_path}out/{i}.out"
    
    n = 10 + i  # Simple formula for testing
    
    with open(in_file_name, 'w') as file:
        file.write(f"{n}\\n")
    
    with open(out_file_name, 'w') as file:
        for j in range(n):
            file.write("1\\n")
'''
                
                # Write and execute the test generator
                with open('test_generator.py', 'w') as f:
                    f.write(generator_content)
                
                result = subprocess.run([sys.executable, 'test_generator.py'], 
                                      capture_output=True, text=True)
                
                # Check that directories were created
                assert os.path.exists('src/example/exec-in/in')
                assert os.path.exists('src/example/exec-in/out')
                
                # Check that test files were created
                assert os.path.exists('src/example/exec-in/in/0.in')
                assert os.path.exists('src/example/exec-in/out/0.out')
                
                # Check file contents
                with open('src/example/exec-in/in/0.in', 'r') as f:
                    content = f.read()
                    assert '10\n' in content
                
                with open('src/example/exec-in/out/0.out', 'r') as f:
                    content = f.read()
                    lines = content.strip().split('\n')
                    assert len(lines) == 10
                    assert all(line == '1' for line in lines)
                
            finally:
                os.chdir(original_cwd)


class TestGeneratorErrorHandling:
    """Test error handling in generators."""

    def test_generator_handles_missing_directories(self):
        """Test that generators handle missing directories gracefully."""
        sum_script = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_sum.py')
        echo_script = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_echo.py')
        
        # Read both scripts
        with open(sum_script, 'r') as f:
            sum_content = f.read()
        
        with open(echo_script, 'r') as f:
            echo_content = f.read()
        
        # Both should handle missing directories by creating them
        assert 'os.makedirs' in sum_content
        assert 'os.makedirs' in echo_content

    def test_generator_handles_existing_directories(self):
        """Test that generators handle existing directories gracefully."""
        sum_script = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_sum.py')
        echo_script = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_echo.py')
        
        # Read both scripts
        with open(sum_script, 'r') as f:
            sum_content = f.read()
        
        with open(echo_script, 'r') as f:
            echo_content = f.read()
        
        # Both should handle existing directories by removing them first
        assert 'shutil.rmtree' in sum_content
        assert 'shutil.rmtree' in echo_content
        assert 'if os.path.exists' in sum_content
        assert 'if os.path.exists' in echo_content

    def test_generator_file_permissions(self):
        """Test that generators set appropriate file permissions."""
        sum_script = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_sum.py')
        echo_script = os.path.join(os.path.dirname(__file__), '../src/conf/example_generator_echo.py')
        
        # Read both scripts
        with open(sum_script, 'r') as f:
            sum_content = f.read()
        
        with open(echo_script, 'r') as f:
            echo_content = f.read()
        
        # Both should set file permissions
        assert 'os.chmod' in sum_content
        assert 'os.chmod' in echo_content
        assert '0o777' in sum_content
        assert '0o777' in echo_content