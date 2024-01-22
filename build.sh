#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run necessary Django commands
python manage.py collectstatic --no-input
python manage.py migrate