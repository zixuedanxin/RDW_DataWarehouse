#!/bin/bash

_DIR="$(cd "$(dirname "$0")" && pwd)"

# predefined values
EDWARE_WORKSPACE=${EDWARE_WORKSPACE:-`cd "$_DIR/../.." && pwd`}
EDWARE_VENV_HOME=${EDWARE_VENV_HOME:-$EDWARE_WORKSPACE/.python-venv}
EDWARE_INI_SOURCE=${EDWARE_INI_SOURCE:-$_DIR/ini}
EDWARE_INI_HOME=${EDWARE_INI_HOME:-$EDWARE_WORKSPACE/config}
EDWARE_LOG_HOME=${EDWARE_LOG_HOME:-$EDWARE_WORKSPACE/logs}

# UDL
EDWARE_INI_UDL=${EDWARE_INI_UDL:-udl2_conf.ini}
EDWARE_UDL_FILES_DEST=${EDWARE_UDL_FILES_DEST:-/opt/edware/zones/landing/arrivals/cat}
EDWARE_VENV_UDL=${EDWARE_VENV_UDL:-$EDWARE_VENV_HOME/udl}
EDWARE_LOG_UDL=${EDWARE_LOG_UDL:-$EDWARE_LOG_HOME/udl.log}

# Smarter
EDWARE_INI_SMARTER=${EDWARE_INI_SMARTER:-development.ini}
EDWARE_VENV_SMARTER=${EDWARE_VENV_SMARTER:-$EDWARE_VENV_HOME/smarter}
EDWARE_LOG_SMARTER=${EDWARE_LOG_SMARTER:-$EDWARE_LOG_HOME/smarter.log}

# HPZ
EDWARE_HPZ_INI=${EDWARE_HPZ_INI:-development_hpz.ini}
EDWARE_VENV_HPZ=${EDWARE_VENV_HPZ:-$EDWARE_VENV_HOME/hpz}
EDWARE_LOG_HPZ=${EDWARE_LOG_HPZ:-$EDWARE_LOG_HOME/hpz.log}

# TSB
EDWARE_TSB_INI=${EDWARE_TSB_INI:-development_tsb.ini}
EDWARE_VENV_TSB=${EDWARE_VENV_TSB:-$EDWARE_VENV_HOME/tsb}
EDWARE_LOG_TSB=${EDWARE_LOG_TSB:-$EDWARE_LOG_HOME/tsb.log}

# Edmigrate
EDWARE_VENV_EDMIGRATE=${EDWARE_VENV_EDMIGRATE:-$EDWARE_VENV_HOME/edmigrate}
EDWARE_LOG_EDMIGRATE=${EDWARE_LOG_EDMIGRATE:-$EDWARE_LOG_HOME/edmigrate.log}

# PREPDF
EDWARE_LOG_PREPDF=${EDWARE_LOG_PREPDF:-$EDWARE_LOG_HOME/prepdf.log}

# unit tests
EDWARE_VENV_BASKET=${EDWARE_VENV_BASKET:-$EDWARE_VENV_HOME/basket}

# autoamtion tests
EDWARE_VENV_TESTS=${EDWARE_VENV_TESTS:-$EDWARE_VENV_HOME/tests}

list_variables(){
    echo "List of environment variables (you can rewrite any of them):"
    for var in ${!EDWARE_@}; do
        eval "_value=\$$var"
        echo "    $var = $_value"
    done
}
