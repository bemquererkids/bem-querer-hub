# Build stage
FROM node:20-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx config template to the templates directory
# Nginx 1.19+ entrypoint automatically performs envsubst on files in /etc/nginx/templates/
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Default port fallback
ENV PORT=8080

# Use default entrypoint and command from nginx:alpine
