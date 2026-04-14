FROM nginx:1.27-alpine

COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY apps/group_class_frontend /usr/share/nginx/html

EXPOSE 80
