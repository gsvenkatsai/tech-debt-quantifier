Gemini said

Step 1: Backend Requirements
PowerShell
pip freeze > backend/requirements.txt


Step 2: Windows Setup Script (setup_env.bat)
Code snippet
@echo off
python -m venv backend\venv
call backend\venv\Scripts\activate
pip install -r backend\requirements.txt
cd backend\repos\requests
pip install -e .
cd ..\..\..\
pause


Step 3: Linux/macOS Setup Script (setup_env.sh)
Bash
#!/bin/bash
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt
cd backend/repos/requests
pip install -e .
cd ../../../


Step 4: Running the Analysis (Windows)
PowerShell
.\backend\venv\Scripts\activate
python -m services.pipeline_service


Step 5: Running the Analysis (Linux/macOS)
Bash
chmod +x setup_env.sh
./setup_env.sh
source backend/venv/bin/activate
python3 -m services.pipeline_service