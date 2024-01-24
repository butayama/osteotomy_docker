FROM python:3.12-slim-bookworm

# Install gcc, necessary libraries, and clean up afterwards
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev \
 && rm -rf /var/lib/apt/lists/*

RUN adduser --debug --disabled-password flask_app

WORKDIR usr/src/flask_app

COPY common.txt .
COPY docker.txt .

RUN pip install --no-cache-dir -r docker.txt

COPY . .
ENV FLASK_APP app.py # Nicht sicher ob erforderlich. Wie weiss Docker, dass osteotomy.py zu starten ist??
# siehe Zuordnung in wsgi.py !
RUN chown -R flask_app:flask_app ./

# RUN chown -R osteotomy:osteotomy ./
USER flask_app
