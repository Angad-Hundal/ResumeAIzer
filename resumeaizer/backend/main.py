from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import pdf_parser

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    pdf_parser.router,
    prefix="/pdf",
    tags=["PDF Processing"],
    responses={404: {"description": "Not found"}}
)