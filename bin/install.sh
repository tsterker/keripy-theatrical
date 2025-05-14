#!/usr/bin/env bash

set -ueEo pipefail

# Config
############################################################################################
KERI_THEATRICAL_PATH="${KERI_THEATRICAL_PATH:?\e[31mMissing KERI_THEATRICAL_PATH\e[0m}"

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
    pip list --editable | grep $KERI_THEATRICAL_PATH || pip install -e "$KERI_THEATRICAL_PATH"
    python -m keripy_theatrical.install
}

# Main
############################################################################################
if [ ! -d "$KERI_THEATRICAL_PATH" ]; then
    print_error "The specified path for keripy-theatrical does not exist: $KERI_THEATRICAL_PATH"
    exit 1
fi

ensure_keripy_theatrical