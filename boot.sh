#!/bin/bash

echo "Running pre-start deployment tasks..."

# Check if the migrations folder exists; if not, initialize it
if [ ! -d "migrations" ]; then
  echo "Migrations folder not found. Initializing..."
  flask db init
fi

# Run migrations
flask db migrate -m "Initial migration" || echo "No migrations to apply"
flask db upgrade || echo "Database already up to date"

# Start the Gunicorn server
echo "Starting Flask app with Gunicorn..."
exec gunicorn -w 4 -b 0.0.0.0:8000 --access-logfile - --error-logfile - flask_app.app:app