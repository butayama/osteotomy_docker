Chat 'ChatTitle(text=Installing Mediawiki on Debian server with Flask+NGINX, isCustom=true)' (b362b514-3a79-49aa-b79f-0143573ed378)
Context:
You are working on project that uses Python Python 3.12.1 language., Installed packages: [Faker, Flask, Flask-Bootstrap, Flask-Consent, Flask-HTTPAuth, Flask-Login, Flask-Mail, Flask-Markdown, Flask-Migrate, Flask-Moment, Flask-PageDown, Flask-SQLAlchemy, Flask-Testing, Flask-WTF, Jinja2, Mako, Markdown, MarkupSafe, PyMySQL, PySocks, Pygments, SQLAlchemy, WTForms, Werkzeug, alembic, ansimarkup, atomicwrites, attrs, bleach, blinker, certifi, chardet, charset-normalizer, click, colorama, coverage, defusedxml, dominate, flask-nav, greenlet, h11, html5lib, httpie, idna, iniconfig, itsdangerous, markdown-it-py, mdurl, more-itertools, multidict, outcome, packaging, pip, pluggy, py, pyparsing, pytest, python-dateutil, python-dotenv, python-editor, requests, requests-toolbelt, rich, selenium, setuptools, six, sniffio, sortedcontainers, text-unidecode, trio, trio-websocket, typing_extensions, urllib3, visitor, waitress, wcwidth, webencodings, wsproto]..
Messages: 2
===================================================================================================================================

User: 
I have a flask nginx webpage on a debian server. On this server I would like to install a mediawiki application. I Would like to be able to reach the mediawiki page independent from the already existing webpage. How do I have to install mediawiki and how di I have to modify routes in nginx?

Assistant: 
Installing MediaWiki on a Debian server running NGINX would involve the following steps:

1. **Ensure the Prerequisites are Installed:**

Before you start, ensure that the LEMP stack is present on your server. This includes Linux, NGINX, MySQL (or MariaDB) and PHP. If not installed, they can be obtained using the package management system `apt`.

```bash
sudo apt install nginx mysql-server php-fpm php-mysql
```

2. **Download and Extract MediaWiki:**

Download the latest version of MediaWiki from the official site into the `/var/www/html` directory and extract it.

```bash
cd /var/www/html
wget https://releases.wikimedia.org/mediawiki/1.35/mediawiki-1.35.1.tar.gz
tar -xvzf mediawiki-*.tar.gz
```

You might want to rename the extracted directory to something simpler, like `mediawiki`.

3. **Create a MySQL Database and User for MediaWiki:**

Log into MySQL and create a new database and user.

```bash
mysql -u root -p
CREATE DATABASE mediawiki;
CREATE USER `wikiuser`@`localhost` IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON mediawiki.* TO `wikiuser`@`localhost`;
EXIT;
```

Replace `'password'` with a stronger password.

4. **Configure NGINX for MediaWiki:**

You will need to add a new server block to your NGINX configuration file or create a new configuration file in `/etc/nginx/sites-available/` and symlink it to `/etc/nginx/sites-enabled/`. 

Below is an example. Replace `mediawiki.mydomain.com` with your chosen domain name.

```nginx
server {
    listen 80;
    server_name mediawiki.mydomain.com;
    root /var/www/html/mediawiki;

    location / {
        index index.php;
        try_files $uri $uri/ @rewrite;
    }

    location @rewrite {
        rewrite ^/(.*)$ /index.php;
    }

    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php7.0-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }
}
```

After editing, check if the NGINX configuration is correct:

```bash
sudo nginx -t
```

If it's fine, reload the NGINX service:

```bash
sudo systemctl reload nginx
```

5. **Set Up MediaWiki:**

Now that your server is ready, access the setup script via your browser by navigating to `http://mediawiki.mydomain.com/mw-config/index.php`. Follow the instructions on the page. You will need the database name, user name, and password you created earlier.

After the setup is complete, you should be able to access your MediaWiki site independently from your flask NGINX web page.

