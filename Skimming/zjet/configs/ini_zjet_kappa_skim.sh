#!/bin/bash
# get path of script directory
if [ ! -z "$ZSH_VERSION" ]; then
    this_file="${(%):-%x}"
else
    this_file="${BASH_SOURCE[0]}"
fi

SCRIPT_DIRECTORY=$(dirname ${this_file})
DIRECTORY_PATH=$(readlink -f ${SCRIPT_DIRECTORY})

echo "Set up user specific Kappa settings!"

USER_CONFIG="${DIRECTORY_PATH}/user_configs/gc_${USER}.cfg"
DEFAULT_USER_CONFIG="${DIRECTORY_PATH}/user_configs/gc_default_user.cfg"

if [ -f "${USER_CONFIG}" ]; then
    echo "Using dedicated user config \"${USER_CONFIG}\"!"
    export KAPPA_USER_CONFIG=${USER_CONFIG}
else
    echo "Dedicated user config \"${USER_CONFIG}\" does not exist!"
    export KAPPA_USER_CONFIG=${DEFAULT_USER_CONFIG}
    echo "Please consider that default grid-contol user settings will be used!"
fi
