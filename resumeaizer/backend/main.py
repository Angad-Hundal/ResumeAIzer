from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import resume

app = FastAPI(
    title="ResumeAizer API",
    description="API for processing resumes with job descriptions",
    version="0.1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "ResumeAizer API is running"}