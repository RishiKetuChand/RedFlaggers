# Build stage
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files first for better cache usage
COPY package*.json ./

# Install ALL deps (include devDependencies like react-scripts)
RUN npm ci

# Copy the rest of the source
COPY . .

ENV REACT_APP_API_BASE_URL=http://backend-svc:8080
# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets only
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

