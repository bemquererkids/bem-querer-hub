# Build stage
FROM node:20-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .

# Pass environment variables to build context
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_KEY
ARG VITE_API_URL

ENV VITE_SUPABASE_URL=$VITE_SUPABASE_URL
ENV VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_KEY
ENV VITE_SUPABASE_KEY=$VITE_SUPABASE_KEY
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx config template to the templates directory
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Default port fallback
ENV PORT=8080
