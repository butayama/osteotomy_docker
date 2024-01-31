# Surces:
https://tutorial-academy.com/uwsgi-nginx-flask-python-sqlite-docker-example/  

https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xix-deployment-on-docker-containers  

`RUN adduser --debug --disabled-password osteotomy`

# --debug  entspricht -D ?!
#           ausführliche Fehlermeldungen ausgeben; nützlich, wenn Probleme mit  adduser  gelöst
#           werden sollen
# --disabled-password
#           Bei der Einrichtung des Nutzers wird nicht nach dem Passwort gefragt.
#           Der Nutzer kann sich nicht am System anmelden, bis ein Passwort mit Hilfe des Befehls passwd gesetzt wird.
#           Dies ist dann z.B. sinnvoll, wenn man als Systemadministrator das Passwort des Nutzers nicht kennen möchte.

`WORKDIR /home/osteotomy`

The WORKDIR command sets a default directory where the application is going to be installed. The new default directory 
is going to apply to any remaining commands in the Dockerfile, and also later when the container is executed.

`COPY /requirements/common.txt common.txt`  

`COPY /requirements/docker.txt docker.txt`  

The COPY command transfers files from your machine to the container file system. This command takes two or more 
arguments, the source and destination files or directories. The source file(s) must be relative to the directory 
where the Dockerfile is located. The destination can be an absolute path, or a path relative to the directory that 
was set in a previous WORKDIR command.

## gunicorn
 I have added gunicorn to my __docker.txt__ file.  
 


 
`COPY app app`  
`COPY migrations migrations`  
`COPY osteotomy.py config.py boot.sh ./`  

The three COPY commands that follow install the application in the container, by copying the app package, 
the migrations directory with the database migrations, and the osteotomy.py and config.py scripts from the top-level 
directory. I'm also copying a new file, boot.sh that I will discuss below.  

`RUN chmod +x boot.sh`

The RUN chmod command ensures that this new boot.sh file is correctly set as an executable file. If you are in a Unix 
based file system and your source file is already marked as executable, then the copied file will also have the 
executable bit set. I added an explicit set because on Windows it is harder to set executable bits. 
If you are working on Mac OS X or Linux you probably don't need this statement, but it does not hurt to have it anyway.  

`ENV FLASK_APP osteotomy.py`  

The ENV command sets an environment variable inside the container. I need to set FLASK_APP, which is required to use 
the flask command.

`RUN chown -R osteotomy:osteotomy ./`

The RUN chown command that follows sets the owner of all the directories and files that were stored in 
/home/osteotomy as the new osteotomy user. Even though I created this user near the top of the Dockerfile, 
the default user for all the commands remained root, so all these files need to be switched to the osteotomy user 
so that this user can work with them when the container is started.  


`USER osteotomy`  

The USER command in the next line makes this new osteotomy user the default for any subsequent instructions, 
and also for when the container is started.

`EXPOSE 5000`  

The EXPOSE command configures the port that this container will be using for its server. This is necessary so 
that Docker can configure the network in the container appropriately. I've chosen the standard Flask port 5000, 
but this can be any port.

`ENTRYPOINT ["./boot.sh"]`  

Finally, the ENTRYPOINT command defines the default command that should be executed when the container is started. 
This is the command that will start the application web server. To keep things well organized, 
I decided to create a separate script for this, and this is the boot.sh file that I copied to the container earlier. 
Here are the contents of this script:

`#!/bin/sh`  
`flask db upgrade`  
`flask translate compile`  
`exec gunicorn -b :5000 --access-logfile - --error-logfile - osteotomy:app`  

I activate the virtual environment, upgrade the database though the migration framework, compile the language 
translations, and finally run the server with gunicorn.

Note the exec that precedes the gunicorn command. In a shell script, exec triggers the process running the script to be 
replaced with the command given, instead of starting it as a new process. This is important, because Docker 
associates the life of the container to the first process that runs on it. In cases like this one, where the start 
up process is not the main process of the container, you need to make sure that the main process takes the place of 
that first process to ensure that the container is not terminated early by Docker.

An interesting aspect of Docker is that anything that the container writes to stdout or stderr will be captured and 
stored as logs for the container. For that reason, the --access-logfile and --error-logfile are both configured with 
a -, which sends the log to standard output so that they are stored as logs by Docker.

With the Dockerfile created, I can now build a container image:  