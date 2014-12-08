#! /bin/bash

OLDPWD=$(pwd)

SOURCE=${BASH_SOURCE[0]}

if [[ "XX$SOURCE" = "XX" ]]; then
    SOURCE=$0
fi

DIR=$( cd "$( dirname "$SOURCE" )" && pwd )
VENV_DIR=$DIR/venv
cd "$DIR"


function missing() {
    hash $1 2>/dev/null
    if [[ $? -eq 1 ]]; then
        # Apparently 0 is true.
        return 0
    else
        return 1
    fi
}

function install() {
    # `pip show` outputs nothing if the package is not installed.
    if [[ `pip show $1` == "" ]]; then
        pip install $1
    fi
}

if missing pip; then
    echo "Please install pip before running this."
    return
fi


if missing virtualenv; then
    # Virtual environment install.
    pip install virtualenv
fi

if [ ! -d "$VENV_DIR" ]; then
    # Create a new environment.
    virtualenv -p `which python2.7` $VENV_DIR
    # And configure it to use python 2.7
fi

if [[ $VIRUTAL_ENV != $DIR* ]]; then
    # Activate if not already active.
    source $VENV_DIR/bin/activate >/dev/null 2>&1
fi

install twisted
install sphinx
install networkx
install matplotlib

# Return to old directory.
cd $OLDPWD

echo "Virtual Environment all configured."
# echo " If this was run using source; then everything is ready."
# echo ""
# echo "      source $0"
# echo ""
echo "To deactivate run"
echo ""
echo "      deactivate"
echo ""
