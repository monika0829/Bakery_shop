#!/bin/bash
# Start script for Goodluck Bakery Django Application

cd /workspace

# Activate virtual environment
source venv/bin/activate

# Collect static files
python manage.py collectstatic --noinput 2>/dev/null || true

# Apply any pending migrations
python manage.py migrate --noinput 2>/dev/null || true

# Start Django with gunicorn in production
# For development, use runserver
if [ "$DEBUG" = "True" ]; then
    echo "Starting Django development server..."
    exec python manage.py runserver 0.0.0.0:8000
else
    echo "Starting Django with gunicorn..."
    exec gunicorn goodluck_bakery.wsgi:application --bind 0.0.0.0:8000 --workers 3
fi
