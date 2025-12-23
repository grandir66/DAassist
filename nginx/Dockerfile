# Build frontend
FROM node:18-alpine AS builder

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Nginx
FROM nginx:alpine

# Copy built frontend
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
