@echo off
echo 🚀 Starting Tech-Debt-Quantifier Setup for Windows...

:: 1. Create Virtual Environment
echo 📦 Creating Virtual Environment...
python -m venv backend\venv

:: 2. Activate and Install Tools
echo 📦 Installing Analysis Engines and Dependencies...
call backend\venv\Scripts\activate
pip install -r backend\requirements.txt

:: 3. Prepare the Target Repo
echo 🔧 Linking 'requests' library for scanning...
cd backend\repos\requests
pip install -e .
cd ..\..\..\

echo ✅ SETUP COMPLETE!
echo To run the analysis, use: python -m services.pipeline_service
pause