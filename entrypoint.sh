#!/bin/sh
set -e

# Load environment
export $(grep -v '^#' .env | xargs)

# Apply database migrations
echo "Applying database migrations..."
flask db upgrade

# Start the Gunicorn server
echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --preload run:app
