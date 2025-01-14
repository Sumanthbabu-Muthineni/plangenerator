from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional
import os
from enum import Enum
import logging
import json
import sys

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

from app.services.floor_plan_generator import FloorPlanGenerator
from app.services.vastu_rule_engine import VastuRuleEngine, Direction, PlotShape, AutoVastuPlan

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FloorPlanRequest(BaseModel):
    plot_direction: str
    plot_width: float = Field(..., gt=0)
    plot_length: float = Field(..., gt=0)
    plot_shape: str
    main_door_position: Optional[str] = None

    @validator('plot_width', 'plot_length')
    def validate_dimensions(cls, v):
        if not isinstance(v, (int, float)):
            raise ValueError('Must be a number')
        if v <= 0:
            raise ValueError('Must be greater than 0')
        return float(v)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Set up the generated_plans directory with absolute path
GENERATED_PLANS_DIR = os.path.join(backend_dir, "generated_plans")
os.makedirs(GENERATED_PLANS_DIR, exist_ok=True)
logger.info(f"Generated plans directory: {GENERATED_PLANS_DIR}")

@app.post("/api/generate-floor-plan")
async def generate_floor_plan(request: FloorPlanRequest):
    try:
        logger.info("Starting floor plan generation")
        logger.info(f"Request data: {request.dict()}")

        # Create AutoVastuPlan instance
        vastu_plan = AutoVastuPlan(
            plot_direction=request.plot_direction,
            plot_width=request.plot_width,
            plot_length=request.plot_length,
            plot_shape=request.plot_shape,
            main_door_position=request.main_door_position
        )
        logger.info(f"Created AutoVastuPlan instance: {vastu_plan}")

        # Initialize VastuRuleEngine and generate room placements
        rule_engine = VastuRuleEngine(vastu_plan)
        logger.info("Initialized VastuRuleEngine")

        # Generate the floor plan with standard layout and validate
        validation_status = rule_engine.validate_plot()
        logger.info(f"Plot validation status: {validation_status}")

        room_placements = rule_engine.generate_floor_plan()
        logger.info(f"Generated room placements: {room_placements}")

        validation_messages = rule_engine.get_validation_messages()
        logger.info(f"Validation messages: {validation_messages}")

        remedies = rule_engine.suggest_remedies()
        logger.info(f"Suggested remedies: {remedies}")

        try:
            # Initialize generator with explicit output directory
            generator = FloorPlanGenerator(output_dir=GENERATED_PLANS_DIR)
            logger.info("Created FloorPlanGenerator")
            
            # Generate the plan
            plan_filename = generator.generate(vastu_plan, room_placements)
            logger.info(f"Generated plan filename: {plan_filename}")
            
            # Verify file creation
            file_path = os.path.join(GENERATED_PLANS_DIR, plan_filename)
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                logger.info(f"File created successfully at {file_path} (size: {file_size} bytes)")
            else:
                raise Exception(f"File not created at {file_path}")

        except Exception as e:
            logger.error(f"Error generating floor plan image: {str(e)}", exc_info=True)
            raise

        response_data = {
            "status": "success",
            "message": "Floor plan generated successfully",
            "plan_details": {
                "plot_width": request.plot_width,
                "plot_length": request.plot_length,
                "direction": request.plot_direction,
                "shape": request.plot_shape,
                "main_door": request.main_door_position,
                "room_placements": room_placements,
                "validation_messages": validation_messages,
                "remedies": remedies,
                "plan_image_url": f"/generated_plans/{plan_filename}"
            }
        }
        
        logger.info(f"Sending response: {response_data}")
        return JSONResponse(content=response_data)

    except Exception as e:
        logger.error(f"Error in request processing: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )

# Mount static files directory
app.mount("/generated_plans", StaticFiles(directory=GENERATED_PLANS_DIR), name="generated_plans")

@app.get("/debug/files")
async def list_files():
    """Debug endpoint to list files in generated_plans directory"""
    try:
        files = os.listdir(GENERATED_PLANS_DIR)
        files_info = []
        for file in files:
            file_path = os.path.join(GENERATED_PLANS_DIR, file)
            files_info.append({
                "name": file,
                "size": os.path.getsize(file_path),
                "created": os.path.getctime(file_path)
            })
        return {
            "directory": GENERATED_PLANS_DIR,
            "files": files_info,
            "file_count": len(files),
            "directory_exists": os.path.exists(GENERATED_PLANS_DIR),
            "directory_writable": os.access(GENERATED_PLANS_DIR, os.W_OK)
        }
    except Exception as e:
        logger.error(f"Error listing files: {e}", exc_info=True)
        return {"error": str(e)}

@app.get("/")
async def root():
    """Root endpoint for API health check"""
    return {
        "status": "healthy",
        "message": "Vastu Floor Plan Generator API is running"
    }

# Optional: Add an endpoint to clean up old generated plans
@app.post("/cleanup-plans")
async def cleanup_old_plans(max_age_hours: int = 24):
    """Clean up floor plan files older than specified hours"""
    try:
        import time
        current_time = time.time()
        cleanup_count = 0
        
        for file in os.listdir(GENERATED_PLANS_DIR):
            file_path = os.path.join(GENERATED_PLANS_DIR, file)
            file_age = current_time - os.path.getctime(file_path)
            if file_age > (max_age_hours * 3600):
                os.remove(file_path)
                cleanup_count += 1
                
        return {
            "status": "success",
            "message": f"Removed {cleanup_count} old floor plan files"
        }
    except Exception as e:
        logger.error(f"Error during cleanup: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)