# Use lightweight Alpine Linux with NGINX
FROM nginx:1.27.3-alpine

# Copy custom NGINX configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy your HTML and JSON files to NGINX's default web root
COPY index.html /usr/share/nginx/html/index.html
COPY data.json /usr/share/nginx/html/data.json
COPY img/ /usr/share/nginx/html/img/

# Expose port 8090
EXPOSE 8090

# Run NGINX in the foreground
CMD ["nginx", "-g", "daemon off;"]
