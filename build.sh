#!/bin/bash

echo "Creating a virtual environment..."
python3.9 -m venv venv
source venv/bin/activate

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing system dependencies..."
sudo apt-get update && sudo apt-get install -y libmysqlclient-dev pkg-config

echo "Installing dependencies from requirements.txt..."
python -m pip install -r requirements.txt

python manage.py collectstatic --noinput
echo "Project build completed!"
