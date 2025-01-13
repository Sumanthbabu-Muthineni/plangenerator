from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.models.floor_plan import FloorPlanRequest
from app.services.floor_plan_generator import FloorPlanGenerator
import os

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory for serving generated images
app.mount("/generated_plans", StaticFiles(directory="generated_plans"), name="generated_plans")

@app.post("/api/generate-floor-plan")
async def generate_floor_plan(request: FloorPlanRequest):
    try:
        generator = FloorPlanGenerator()
        image_path = generator.generate(request)
        # Convert file path to URL
        image_url = f"http://localhost:8000/generated_plans/{os.path.basename(image_path)}"
        return {"image_url": image_url}
    except Exception as e:
        return {"error": str(e)}, 500 