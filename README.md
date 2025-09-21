# AI Startup Analyst Platform
*Team RedFlaggers - Google Gen AI Hackathon Submission*

## 🎯 Problem Statement
Early-stage investors are overwhelmed by unstructured startup data from pitch decks, founder calls, emails, and scattered news reports. Traditional analysis is time-consuming, inconsistent, and prone to missing critical red flags. This platform delivers an AI-powered analyst that cuts through the noise and generates investor-ready insights at scale.

## 🚀 Solution Overview
An AI-powered analyst platform that evaluates startups by synthesizing founder materials and public data to generate concise, actionable investment insights with clear benchmarks and risk assessments.

### Key Capabilities
- **Document Processing**: Ingest pitch decks, call transcripts, founder updates, and emails to generate structured deal notes
- **Benchmarking**: Compare startups against sector peers using financial multiples, hiring data, and traction signals
- **Risk Assessment**: Flag potential indicators like inconsistent metrics, inflated market size, or unusual churn patterns
- **Investment Recommendations**: Generate investor-ready recommendations with customizable weightings

## 🏗️ Architecture

### Frontend
- **Technology**: React.js with modern UI components
- **Features**: Interactive dashboard for uploading documents and viewing analysis results
- **Libraries**: Framer Motion for animations, React Router for navigation

### Backend Services

#### 1. API Gateway
- **Framework**: FastAPI
- **Purpose**: Central entry point for all client requests
- **Features**: Request routing, file upload handling, response aggregation

#### 2. Data Manager
- **Technology**: Python with Google Cloud Storage integration
- **Purpose**: Manages document storage and retrieval on Google Cloud Platform
- **Features**: File upload/download, metadata management, storage optimization

#### 3. Analysis Service (AI Agent)
- **Technology**: Python with Google AI integration
- **Purpose**: Core AI agent for startup evaluation and analysis
- **Features**:
  - Document parsing and content extraction
  - Financial analysis and benchmarking
  - Risk factor identification
  - Investment recommendation generation

#### 4. Infographic Service (AI Agent)
- **Technology**: Python with visualization capabilities
- **Purpose**: Generates visual summaries and infographics from analysis results
- **Features**:
  - Automated chart generation
  - Visual risk assessment displays
  - Investment summary graphics

## 🛠️ Tech Stack

### Google AI Technologies
- **Gemini**: Core AI model for analysis and insights
- **Vertex AI**: Machine learning platform for model deployment
- **Cloud Vision**: Document and image processing
- **BigQuery**: Data warehousing and analytics
- **Cloud Storage**: File storage and management
- **Pub/Sub**: Asynchronous messaging between services

### Additional Technologies
- **Backend**: FastAPI, Python
- **Frontend**: React.js, JavaScript
- **Containerization**: Docker
- **Deployment**: Kubernetes (YAML configs included)
- **Communication**: Google Cloud Pub/Sub for service orchestration

## 🚀 Getting Started

### Prerequisites
- Google Cloud Platform account
- Docker installed
- Node.js and npm
- Python 3.8+

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-repo/RedFlaggers.git
   cd RedFlaggers
   ```

2. **Set up Google Cloud credentials**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
   ```

3. **Start Backend Services**
   ```bash
   # API Gateway
   cd backend/api-gateway
   pip install -r requirements.txt
   python main.py

   # Data Manager
   cd ../data-manager
   pip install -r requirements.txt
   python main.py

   # Analysis Service
   cd ../analysis-service
   pip install -r requirements.txt
   python run.py

   # Infographic Service
   cd ../infographic-service
   pip install -r requirements.txt
   python run.py
   ```

4. **Start Frontend**
   ```bash
   cd frontend
   npm install
   npm start
   ```

### Docker Deployment
Each service includes a Dockerfile for containerized deployment:

```bash
# Build and run with Docker
docker build -t redflaggers-api-gateway backend/api-gateway/
docker run -p 8000:8000 redflaggers-api-gateway
```

### Kubernetes Deployment
Deployment configurations are available in `backend/deployment/`:

```bash
kubectl apply -f backend/deployment/
```

## 📁 Project Structure
```
RedFlaggers/
├── frontend/                 # React.js frontend application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Main application pages
│   │   └── assets/         # Static assets
│   └── package.json
├── backend/
│   ├── api-gateway/        # Central API gateway service
│   ├── data-manager/       # GCS data management service
│   ├── analysis-service/   # AI analysis agent
│   ├── infographic-service/# Visualization agent
│   └── deployment/         # Kubernetes deployment configs
└── README.md
```

## 🎯 Hackathon Submission Details
- **Team**: RedFlaggers
- **Event**: Google Gen AI Hackathon by HackToSkill
- **Category**: AI Analyst for Startup Evaluation
- **Status**: Minimal Viable Prototype

## 🔮 Future Enhancements
- Real-time market data integration
- Advanced sector-specific analysis models
- Interactive dashboard with drill-down capabilities
- Integration with CRM and deal management platforms
- Multi-language support for global startup analysis

## 👥 Team RedFlaggers
Built with passion for transforming startup investment analysis using Google's cutting-edge AI technologies.

---
*This is a prototype submission demonstrating the potential of AI-powered startup evaluation. The platform showcases core functionality and architectural patterns for a production-ready solution.*
