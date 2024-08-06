FROM --platform=linux/arm64 nginx:alpine

# Create necessary directories
RUN mkdir -p /etc/nginx/certs /etc/nginx/conf.d

# Copy configuration files
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/default.conf /etc/nginx/conf.d/default.conf

# Create a directory for Nginx to write runtime files
RUN mkdir -p /var/cache/nginx /var/run /var/log/nginx

# Set correct permissions
RUN chown -R nginx:nginx /etc/nginx && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /var/run

# Change the pid file location in nginx.conf
RUN sed -i 's|pid        /var/run/nginx.pid;|pid        /var/run/nginx.pid;|' /etc/nginx/nginx.conf

# Use NGINX's default entrypoint script
ENTRYPOINT ["/docker-entrypoint.sh"]

# Run Nginx
CMD ["nginx", "-g", "daemon off;"]