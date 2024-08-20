import os
import sys
from pathlib import Path
lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__),  'lib'))
if 'PYTHONPATH' in os.environ:
    os.environ['PYTHONPATH'] = lib_path + os.pathsep + os.environ['PYTHONPATH']
else:
    os.environ['PYTHONPATH'] = lib_path

# make sure that  PYTHONPATH applies in the current session
#sys.path.insert(0, Path(lib_path).parent)
sys.path.insert(0, lib_path)
print(f"PYTHONPATH set to {lib_path}")

from .Quantanium import Quantanium
