@echo off
pwsh -NoProfile -File "%~dp0tools\open-workbench.ps1"
if errorlevel 1 pause
