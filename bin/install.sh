#!/usr/bin/env bash

set -ueEo pipefail

# Config
############################################################################################
DEFAULT_KERI_THEATRICAL_PATH=$(dirname $(dirname ${BASH_SOURCE[0]}))
KERI_THEATRICAL_PATH="${KERI_THEATRICAL_PATH:-$DEFAULT_KERI_THEATRICAL_PATH}"

# Helpers
############################################################################################
print_error () {
    echo -e "\e[31m$1\e[0m"
}

print_info () {
    echo -e "\e[32m$1\e[0m"
}

ensure_keripy_theatrical () {
    set -ue
    set +o pipefail

    print_info "Ensure keripy-theatrical is installed and initialized..."
    python -m pip list --editable | grep $KERI_THEATRICAL_PATH || python -m pip install -e "$KERI_THEATRICAL_PATH"
    python -m keripy_theatrical.install
}

patch_kli () {
    KLI_PATH=$(which kli)

    sed 's/^import sys$/import sys, sitecustomize, usercustomize/' "$KLI_PATH" > "$KLI_PATH.patched"
    mv "$KLI_PATH" "$KLI_PATH.bak"
    mv "$KLI_PATH.patched" "$KLI_PATH"
    chmod +x "$KLI_PATH"
}

# Main
############################################################################################
if [ ! -d "$KERI_THEATRICAL_PATH" ]; then
    print_error "The specified path for keripy-theatrical does not exist: $KERI_THEATRICAL_PATH"
    exit 1
fi

ensure_keripy_theatrical
patch_kli