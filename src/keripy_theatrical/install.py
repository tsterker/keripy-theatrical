"""
# Create a sitecustomize.py that loads Keripy Theatrical
# @see https://docs.python.org/3/library/site.html#module-sitecustomize
"""

import site, os
from .utils import print_yellow

theatrical_package_name = "keripy_theatrical"
sitecustomize_path = os.path.join(site.getsitepackages()[0], "sitecustomize.py")
usercustomize_path = os.path.join(site.getsitepackages()[0], "usercustomize.py")

print_yellow(f"Initializing Keripy Theatrical...")

def write_customize_script(path):
    with open(path, "w") as f:
        f.write(f"import {theatrical_package_name}.theatrical as theatrical\n")
        f.write((
            "try:\n"
            "    theatrical.init()\n"
            "except Exception as e:\n"
            "    import sys, traceback\n"
            "    sys.stderr.write(f'\\033[91m🎭 Error in " + sitecustomize_path + ": {e}\\033[0m\\n')\n"
            "    tb_lines = traceback.format_exception(type(e), e, e.__traceback__)\n"
            "    for line in tb_lines:\n"
            "        sys.stderr.write(f'\\033[91m🎭 {line}\\033[0m')\n"
        ))

print_yellow(f"Writing sitecustomize.py to {sitecustomize_path}")
write_customize_script(sitecustomize_path)

print_yellow(f"Writing usercustomize.py to {usercustomize_path}")
write_customize_script(usercustomize_path)
