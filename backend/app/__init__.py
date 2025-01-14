from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def create_app():
    app = FastAPI(title="Vastu Floor Plan Generator")
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app