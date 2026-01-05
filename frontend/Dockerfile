# Build stage
FROM node:20-alpine AS build

WORKDIR /app

# Build argument for API URL
ARG VITE_API_URL=http://localhost:80
ENV VITE_API_URL=$VITE_API_URL

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm install

# Copy source files
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files to nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
