# AI Startup Analyst

A React-based web application for AI-powered startup analysis and investment insights.

## Features

- **Home Page**: Product overview with features and call-to-action
- **Demo Page**: Interactive demo with file upload and analysis workflow
- **About Page**: Team profiles and company information
- **Responsive Design**: Mobile-friendly interface
- **Smooth Animations**: Professional transitions and effects

## Development

### Prerequisites
- Node.js 18 or higher
- npm or yarn

### Local Development
```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

## Docker Deployment

### Build and Run with Docker
```bash
# Build the Docker image
docker build -t ai-startup-analyst .

# Run the container
docker run -p 3000:80 ai-startup-analyst
```

### Using Docker Compose
```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Production Deployment
```bash
# Build for production
docker build -t ai-startup-analyst:latest .

# Run in production mode
docker run -d \
  --name ai-startup-analyst \
  -p 80:80 \
  --restart unless-stopped \
  ai-startup-analyst:latest
```

## Docker Features

- **Multi-stage build**: Optimized image size using Node.js for build and nginx for serving
- **Nginx configuration**: Custom configuration with compression and caching
- **Health checks**: Built-in health monitoring
- **Security headers**: Enhanced security configuration
- **Single Page Application support**: Proper routing for React Router

## Accessing the Application

Once running, the application will be available at:
- Local development: http://localhost:3000
- Docker container: http://localhost:3000 (or port 80 in production)

## Environment Variables

The application supports the following environment variables:
- `NODE_ENV`: Set to 'production' for production builds

## API Integration

The demo page is configured to work with backend APIs:
- Upload endpoint: `/api/upload`
- Analysis start: `/api/start-analysis`
- Status check: `/api/analysis-status`

Update the API endpoints in the Demo component to match your backend URLs.