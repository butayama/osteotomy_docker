FROM python:3.13-alpine
# docker run command does not succeed 211023
RUN adduser --debug --disabled-password osteotomy

ENV FLASK_APP osteotomy.py
ENV FLASK_CONFIG docker

RUN adduser -D osteotomy
USER osteotomy

WORKDIR /home/osteotomy

COPY /requirements requirements
RUN python -m venv venv
RUN venv/bin/pip install -r requirements/docker.txt

COPY app app
COPY migrations migrations
COPY osteotomy.py config.py boot.sh ./

# COPY . .
RUN chmod +x boot.sh

# remove before deploy
# ENV FLASK_DEBUG=1

RUN chown -R osteotomy:osteotomy ./
USER osteotomy

# runtime configuration
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]