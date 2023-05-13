@echo off

setlocal

echo Starting ...

set VENV_DIR=venv

if exist %VENV_DIR% (call:startEnv) else (call:createEnv)

set defaultPort=8000

set/p port=Port[%defaultPort%]: 

if [%port%] == [] set port=%defaultPort%

set PYTHON_ENV=.\venv\Scripts\activate.bat

set DJANGO_PROJECT=.\manage.py

echo Starting server on port: %port%

echo.

python %DJANGO_PROJECT% runserver %port%

call venv\Scripts\deactivate.bat

endlocal

pause

:createEnv
    echo Creating Python Virtual Environment on .\%VENV_DIR% ...

    pip install virtualenv

    virtualenv %VENV_DIR%

    call venv\Scripts\activate.bat

:startEnv
    echo Starting Python Virtual Environment

    call venv\Scripts\activate.bat

    echo Installing packages

    pip install -r requirements.txt