FROM nginx:stable-alpine@sha256:0985e772fb9f729e6fa0980da05fca5d9c468e870eed43071545afa9d2e27d94

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html 404.html styles.css site.js site.webmanifest favicon.svg flutter.svg og-image.png icon-192.png icon-512.png apple-touch-icon.png robots.txt sitemap.xml llms.txt llms-full.txt humans.txt security.txt /usr/share/nginx/html/
COPY .well-known/security.txt /usr/share/nginx/html/.well-known/security.txt

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1/ || exit 1
