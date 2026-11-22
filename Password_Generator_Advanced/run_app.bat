@echo off
cd /d "%~dp0"
python password_generator.py
if errorlevel 1 pause
