from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class Direction(str, Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    NORTH_EAST = "north_east"
    NORTH_WEST = "north_west"
    SOUTH_EAST = "south_east"
    SOUTH_WEST = "south_west"

class PlotShape(str, Enum):
    RECTANGULAR = "rectangular"
    SQUARE = "square"
    L_SHAPED = "l_shaped"

class Room(BaseModel):
    width: float = Field(..., gt=0, description="Room width in meters")
    length: float = Field(..., gt=0, description="Room length in meters")
    position_x: float = Field(..., description="X coordinate of room position")
    position_y: float = Field(..., description="Y coordinate of room position")
    room_type: str

class AutoVastuPlan(BaseModel):
    plot_direction: Direction
    plot_width: float = Field(..., gt=0)
    plot_length: float = Field(..., gt=0)
    plot_shape: PlotShape
    main_door_position: Optional[Direction] = None