# Build stage
FROM node:18-alpine as build-stage

WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm ci

# Copy the rest of the application code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:stable-alpine as production-stage

# Copy built files from the build stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy nginx configuration for Vue Router
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
