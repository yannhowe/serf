FROM nginx:mainline-alpine
RUN set -x ; \
  addgroup -g 82 -S www-data ; \
  adduser -u 82 -D -S -G www-data www-data && exit 0 ; exit 1
COPY sites-enabled/ /etc/nginx/sites-enabled/
RUN rm -v /etc/nginx/conf.d/default.conf
RUN rm -v /etc/nginx/nginx.conf
COPY conf/nginx.conf /etc/nginx/nginx.conf
COPY www/ /var/www/
RUN chown -R www-data:www-data /var/www/
EXPOSE 80 443
