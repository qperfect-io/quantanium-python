import os
import shutil
import sys
import glob
import subprocess
from pathlib import Path

def find_shared_library(lib_dir):
    """
    Find the compiled .so file in the specified directory.
    
    Args:
        lib_dir (str): The directory where to search for the .so file.
    
    Returns:
        str: Path to the found .so file.
    
    Raises:
        FileNotFoundError: If no .so files are found in the directory.
    """
    so_files = glob.glob(os.path.join(lib_dir, "*.so"))
    if len(so_files) == 0:
        raise FileNotFoundError("No shared library (.so) files found in the specified directory.")
    return so_files[0]  # Assuming there's only one .so file

def install_quantaniumpy_core():
    """
    Install the quantaniumpy_core module using a temporary setup.py file.
    """
    print("Installing quantaniumpy_core...")

    # Define the source directory where the .so file is located
    lib_source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../release-python/lib'))
    print(f"Looking for shared library in {lib_source_dir}...")
    lib_source = find_shared_library(lib_source_dir)

    # Create temporary setup.py content to install quantaniumpy_core
    setup_py_content = f"""
from setuptools import setup, Extension

setup(
    name='quantaniumpy_core',
    version='0.1.0',
    description='Core library for Quantanium',
    ext_modules=[Extension('quantaniumpy_core', sources=[], extra_objects=['{lib_source}'])],
)
"""
    # Write the temporary setup.py file
    setup_py_path = os.path.join(lib_source_dir, 'setup_quantaniumpy_core.py')
    with open(setup_py_path, 'w') as setup_file:
        setup_file.write(setup_py_content)

    # Execute the setup.py to install the quantaniumpy_core module
    print("EXECUTABLE = ", sys.executable)
    subprocess.run([sys.executable, setup_py_path, 'install'], check=True)

    # Remove the temporary setup.py file
    os.remove(setup_py_path)
    print("quantaniumpy_core has been successfully installed.")

def copy_shared_library():
    """
    Copy the compiled .so file to the target directory in the project.
    """
    print("Copy source library from ...")

    # Define the source and target directories for the .so file
    lib_source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../release-python/lib'))
    print(lib_source_dir)
    lib_source = find_shared_library(lib_source_dir)

    lib_target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', 'quantaniumpy', 'lib'))

    # Ensure the target directory exists
    if not os.path.exists(lib_target_dir):
        os.makedirs(lib_target_dir)

    # Copy the .so file to the target directory
    shutil.copy(lib_source, lib_target_dir)
    print(f"Shared library {os.path.basename(lib_source)} copied to {lib_target_dir}")





# Main function to install quantaniumpy_core, copy quantaniumpy C++ library, and adjust PYTHONPATH
def main():
    install_quantaniumpy_core()
    copy_shared_library()

if __name__ == "__main__":
    main()
