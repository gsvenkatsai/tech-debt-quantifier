#!/bin/bash
echo "🚀 Starting Tech-Debt-Quantifier Setup for Linux/macOS..."

# 1. Create Virtual Environment
echo "📦 Creating Virtual Environment..."
python3 -m venv backend/venv

# 2. Activate and Install Tools
echo "📦 Installing Analysis Engines and Dependencies..."
source backend/venv/bin/activate
pip install -r backend/requirements.txt

# 3. Prepare the Target Repo
echo "🔧 Linking 'requests' library for scanning..."
cd backend/repos/requests
pip install -e .
cd ../../../

echo "✅ SETUP COMPLETE!"
echo "To run: source backend/venv/bin/activate && python3 -m services.pipeline_service"