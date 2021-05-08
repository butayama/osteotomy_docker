FROM python:3.8-slim-buster

RUN adduser --debug --disabled-password osteotomy

WORKDIR /home/osteotomy

COPY /requirements/common.txt common.txt
COPY /requirements/docker.txt docker.txt
# RUN python -m venv venv
RUN pip install --upgrade pip
RUN pip install -r docker.txt

COPY app app
COPY ssl ssl
COPY osteotomy.py config.py osteotomy.eu.csr gunicorn.conf.py boot.sh ./

# COPY . .
RUN chmod +x boot.sh

ENV FLASK_APP osteotomy.py
# ENV FLASK_CONFIG=development

# remove before deploy
# ENV FLASK_DEBUG=1

RUN chown -R osteotomy:osteotomy ./
USER osteotomy

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]