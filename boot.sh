#!/bin/sh
source venv/bin/activate
flask deploy
# flask db upgrade
# flask translate compile
exec gunicorn -b 0.0.0.0:5000 --access-logfile - --error-logfile - osteotomy:app
