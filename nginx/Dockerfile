FROM nginx:1.15.8

COPY .ssl/certs/chain_123.crt /etc/ssl/certs/
COPY .ssl/private/osteotomy.eu.key /etc/ssl/private/
RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/
RUN rm /etc/nginx/conf.d/default.conf
COPY project.conf /etc/nginx/conf.d/

