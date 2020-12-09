FROM python:3.8-slim-buster

RUN adduser --debug --disabled-password osteotomy
# --debug
#           ausführliche Fehlermeldungen ausgeben; nützlich, wenn Probleme mit  adduser  gelöst
#           werden sollen
# --disabled-password
#           Bei der Einrichtung des Nutzers wird nicht nach dem Passwort gefragt.
#           Der Nutzer kann sich nicht am System anmelden, bis ein Passwort mit Hilfe des Befehls passwd gesetzt wird.
#           Dies ist dann z.B. sinnvoll, wenn man als Systemadministrator das Passwort des Nutzers nicht kennen möchte.

WORKDIR /home/osteotomy

COPY /requirements/common.txt common.txt
COPY /requirements/docker.txt docker.txt
# RUN python -m venv venv
RUN pip install --upgrade pip
RUN pip install -r docker.txt

COPY app app
COPY migrations migrations
COPY osteotomy.py config.py boot.sh ./

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