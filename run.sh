#!/bin/bash

echo Starting ...

VENV_DIR=venv

if [ -d "$VENV_DIR" ]
then
    source venv/Scripts/activate
else
    echo Creating Python Virtual Environment on ./$VENV_DIR ...

    pip install virtualenv

    virtualenv $VENV_DIR

    source venv/Scripts/activate

    echo Installing packages

    pip install -r requirements.txt
fi

read -p "Port[8000]: " port
port=${port:-8000}

echo Starting server on port: $port

python manage.py runserver $port

deactivate

echo Done

read -n1 -r -p "Press any key to exit..." key