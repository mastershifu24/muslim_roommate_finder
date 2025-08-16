#!/bin/bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r config/requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate

# Run the server with Gunicorn, using the port Render provides
gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}
