#!/bin/sh

# Exit immediately if any command fails
set -e

# Apply database migrations
echo "Applying database migrations..."
flask db upgrade

# Start the Gunicorn server to run the application
echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --preload run:app
