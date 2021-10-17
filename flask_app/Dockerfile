FROM python:3.8-slim-buster

RUN adduser --debug --disabled-password flask_app

WORKDIR usr/src/flask_app

COPY common.txt .
COPY docker.txt .

RUN pip install --no-cache-dir -r docker.txt

COPY . .
ENV FLASK_APP osteotomy.py # Nicht sicher ob erforderlich. Wie weiss Docker, dass osteotomy.py zu starten ist??
RUN chown -R flask_app:flask_app ./

# RUN chown -R osteotomy:osteotomy ./
USER flask_app
