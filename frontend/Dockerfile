FROM nginx:1.27-alpine
COPY frontend/index.html frontend/favicon.svg frontend/styles.css frontend/tokens.css frontend/base.css /usr/share/nginx/html/
COPY frontend/views/ /usr/share/nginx/html/views/
COPY frontend/src/ /usr/share/nginx/html/src/
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
