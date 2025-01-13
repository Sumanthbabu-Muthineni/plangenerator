from pydantic import BaseModel
from typing import List, Optional

class Room(BaseModel):
    width: float
    length: float
    position_x: float
    position_y: float
    room_type: str

class FloorPlanRequest(BaseModel):
    width: float
    length: float
    scale: float
    rooms: List[Room]
    style: Optional[str] = "pencil" 