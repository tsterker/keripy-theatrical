"""
# Create a sitecustomize.py that loads Keripy Theatrical
# @see https://docs.python.org/3/library/site.html#module-sitecustomize
"""

import site, os
from .utils import print_yellow

theatrical_package_name = "keripy_theatrical"
sitecustomize_path = os.path.join(site.getsitepackages()[0], "sitecustomize.py")

print_yellow(f"Initializing Keripy Theatrical...")
print_yellow(f"Writing sitecustomize.py to {sitecustomize_path}")

with open(sitecustomize_path, "w") as f:
    f.write(f"import {theatrical_package_name}.theatrical as theatrical\n")
    f.write("theatrical.apply_patches()\n")