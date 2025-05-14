import json
import sys

THEATRICAL_PATCH_MARKER = "THEATRICAL_PATCHED"

def log(text = '', prefix='', end='\n'):
    lines = text.splitlines()

    for line in lines:
        print(f"🎭 {prefix}{line}", end=end, file=sys.stderr)

    if len(lines) == 0:
        print(f"🎭 {prefix}", end=end, file=sys.stderr)

def print_blue(text, prefix='', end='\n'):
    log(f"\033[94m{text}\033[0m", prefix, end)

def print_green(text, prefix='', end='\n'):
    log(f"\033[92m{text}\033[0m", prefix, end)

def print_yellow(text, prefix='', end='\n'):
    log(f"\033[93m{text}\033[0m", prefix, end)

def print_red(text, prefix='', end='\n'):
    log(f"\033[91m{text}\033[0m", prefix, end)

def print_purple(text, prefix='', end='\n'):
    log(f"\033[95m{text}\033[0m", prefix, end)

def print_cyan(text, prefix='', end='\n'):
    log(f"\033[96m{text}\033[0m", prefix, end)

def print_dim(text, prefix='', end='\n'):
    log(f"\033[90m{text}\033[0m", prefix, end)


def dump_call_stack():
    import inspect

    prefix = '> '
    print_purple(f"{prefix}Full call Stack:")
    for frame in inspect.stack():
        print_purple(f"{prefix}{frame.filename}:{frame.lineno}")

def dump_caller():
    import inspect

    for frame in inspect.stack():
        if 'keripy_theatrical' in frame.filename:
            continue

        print_purple(f"> Last non-theatrical frame: {frame.filename}:{frame.lineno}")
        break

def dump(label, data):
    log();
    log(f"=========================== {label} ==================================================================")
    dump_caller()
    log(json.dumps(data, sort_keys=True, indent=4))
    print(f"======================================================================================================")

def throw(message):
    raise Exception(f"\033[91m[🎭 keripy-theatrical 🎭] {message}\033[0m")