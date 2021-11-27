#!/bin/sh
# Use notepad++, go to edit -> EOL conversion -> change from CRLF to LF. (
# see: https://stackoverflow.com/questions/51508150/standard-init-linux-go190-exec-user-process-caused-no-such-file-or-directory
source venv/bin/activate
flask deploy
# flask db upgrade
# flask translate compile
exec gunicorn -b 0.0.0.0:5000 --access-logfile - --error-logfile - osteotomy:flask_app
