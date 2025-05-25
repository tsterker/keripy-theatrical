# Keripy Theatrical

A hacky python and bash script suite to make [`keripy`](https://github.com/WebOfTrust/keripy) more "theatrical" by logging expressively and possibly even throwing exceptions when things don't go the happy path.

The package where keripy-theatrical is "installed" into is referred to as the "target" or the "host".

Note that the host project does not need to be the `keripy` package itself, but it could be any project utilizing `keripy` as a dependency.

> ![Theatrical Output Screenshot](./docs/screenshot.png)

## Installation

In order to use this package, you need install it into an existing project that uses `keripy`.

Installation is currently done by checking out this `keripy-theatrical` repo and running the [./bin/install.sh](bin/install.sh) script from within your target project.

**Example:**
```bash
# Clone the keripy-theatrical repo
export THEATRICAL_PATH=$HOME/Downloads/keripy-theatrical
git clone git@github.com:tsterker/keripy-theatrical.git $THEATRICAL_PATH

# Clone your KERI project (e.g. keripy)
export KERI_PATH=$HOME/Downloads/keripy
git clone git@github.com:WebOfTrust/keripy.git $KERI_PATH

# Install theatrical into your KERI project
cd $KERI_PATH
uv pip install -e .
uv pip install pip
uv run bash $THEATRICAL_PATH/bin/install.sh

# Confirm it's working by seeing the theatrical log output prefixed with 🎭
uv run kli init --name foo --nopasscode
uv run kli ipex grant --name=foo --alias=foo --said=foo --recipient=foo
```

## Usage

Generally, the keripy-theatrical package is currently expected to be cloned and then manually edited as needed, as you debug/trace/monkey-patch the KERI project you're using.

There is no clear structure for how things are set up and (dead) code is currently added as needed during my mostly clueless explorations.

Some general pointers:

- Check the [theatrical.init](src/keripy_theatrical/theatrical.py) to see which namespaces are currently traced and/or "tapped".
- Check the [keripy patcher](src/keripy_theatrical/patchers/keripy.py) to see some more involved/specialized monkey-patching.
- Note note all keripy-theatrical output is sent to STDERR to not interfere with any STDOUT that the patched code might produce and/or rely on. If you want to grep the theatrical output make sure to redirect STDERR to STDOUT like so:
  ```bash
  uv run kli init --name bar --nopasscode 2>&1 | rg configing
  ```
