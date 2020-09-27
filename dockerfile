FROM python:3.8-slim-buster

RUN adduser --disabled-password osteotomy

WORKDIR /home/osteotomy

COPY /requirements/common.txt common.txt
COPY /requirements/docker.txt docker.txt
RUN python -m venv venv
RUN venv/bin/pip install -r docker.txt

COPY app app
COPY migrations migrations
COPY osteotomy.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP osteotomy.py

RUN chown -R osteotomy:osteotomy ./
USER osteotomy

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]