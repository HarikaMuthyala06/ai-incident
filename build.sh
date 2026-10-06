#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "============================================="
echo "Building Frontend (React + Vite + Tailwind)"
echo "============================================="
cd frontend
npm install
npm run build
cd ..

echo "============================================="
echo "Installing Backend Dependencies (FastAPI)"
echo "============================================="
cd backend
pip install --upgrade pip
pip install -r requirements.txt
cd ..

echo "============================================="
echo "Build Successful! Ready for Deployment."
echo "============================================="
