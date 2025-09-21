from fastapi import FastAPI
from routers import Routers
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Analyst API Gateway")

# Configure CORS
origins = [
    "http://34.40.32.78/",
    "http://34.40.32.78:80",
    "http://172.27.173.134:3000",
    "http://172.27.173.59:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         #["*"] 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(Routers.router)
