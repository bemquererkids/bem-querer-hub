FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Install serve to run the static files
RUN npm install -g serve

# Serve the app
CMD sh -c "serve -s dist -l $PORT"
