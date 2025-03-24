#!/bin/bash

set -e

echo "Waiting for postgres..."

# Check Google API key
if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your-google-api-key" ] || [ "$GOOGLE_API_KEY" = "your-google-api-key-here" ]; then
  echo "WARNING: Valid Google API key not detected. The document parsing functionality will not work."
  echo "Please set the GOOGLE_API_KEY environment variable to a valid Google API key."
  echo "You can create one at https://makersuite.google.com/app/apikey"
fi

echo "Running migrations..."
# First, migrate the auth app to create auth_user table
python manage.py migrate auth
# Then migrate the rest
python manage.py migrate
# Make sure all app migrations are detected
python manage.py makemigrations
# Apply any newly created migrations
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting application..."
gunicorn --bind 0.0.0.0:8000 config.wsgi
