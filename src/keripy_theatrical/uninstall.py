"""
# Remove sitecustomize.py
"""

import site, os
from .utils import print_yellow

theatrical_package_name = "keripy_theatrical"
sitecustomize_path = os.path.join(site.getsitepackages()[0], "sitecustomize.py")

print_yellow(f"Removing sitecustomize.py from {sitecustomize_path}")

os.remove(sitecustomize_path)