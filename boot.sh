#!/bin/sh
# flask db upgrade
# flask translate compile
# gunicorn documentation: https://docs.gunicorn.org/en/stable/run.html
exec gunicorn -b :5000 --access-logfile - --error-logfile - osteotomy:app
# exec gunicorn osteotomy:app
