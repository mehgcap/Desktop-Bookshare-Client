@echo off
cd c:\prog\bookshare\dbc
echo Compiling
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist output rd /s /q output
python setup.py py2exe>py2exe_log.txt 2> py2exe_errors.txt 
if exist dist\w9xpopen.exe del dist\w9xpopen.exe
if exist dist echo Done building, running Inno Setup...
"C:\Program Files (x86)\Inno Setup 5\Compil32.exe" /cc setup.iss 
if exist output echo Done!