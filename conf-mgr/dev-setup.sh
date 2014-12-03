#! /bin/bash

SOURCE=${BASH_SOURCE[0]}
DIR=$( cd "$( dirname "$SOURCE" )" && pwd )
VENV_DIR=venv
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


if missing "virtualenv"; then
    # Virtual environment install.
    pip install virtualenv
fi

if [ ! -d "$VENV_DIR" ]; then
    # Create a new environment.
    virtualenv -p `which python2.7` $VENV_DIR
    # And configure it to use python 2.7
fi

if [[ $VIRUTAL_ENV != $DIR* ]]; then
    source $VENV_DIR/bin/activate >/dev/null 2>&1
fi

if missing twistd ; then
    pip install twisted
fi

if missing sphinx-build ; then
    pip install sphinx
fi



echo "Virtual Environment all configured. Now run the following to activate it:"
echo ""
echo "      source $VENV_DIR/bin/activate"
echo ""
echo "Or run the whole thing in one command:"
echo ""
echo "      source $0"
echo ""
