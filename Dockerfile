FROM python:3.8-alpine
# local testrun failes 31.10.21 15:05

ENV FLASK_APP osteotomy.py
ENV FLASK_CONFIG docker
# remove before deploy
# ENV FLASK_DEBUG=1

# https://stackoverflow.com/questions/36710459/how-do-i-make-a-comment-in-a-dockerfile

RUN apk update && apk --no-cache add g++ musl-dev && rm -rf /var/lib/apt/lists/*
RUN apk add linux-headers
RUN apk add libffi-dev

RUN adduser -D flask_osteotomy
# USER flask_osteotomy

WORKDIR /home/osteotomy

COPY /requirements requirements
ENV DEBIAN_FRONTEND noninteractive
RUN python -m venv venv
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install wheel
RUN venv/bin/pip install -r requirements/docker.txt

COPY flask_app flask_app
COPY migrations migrations
COPY osteotomy.py config.py boot.sh ./

# COPY . .
RUN chmod +x boot.sh
RUN chown -R flask_osteotomy:flask_osteotomy ./

USER flask_osteotomy

# runtime configuration
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]