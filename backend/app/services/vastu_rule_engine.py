from enum import Enum
from typing import List, Dict, Tuple, Optional
import numpy as np
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

class AutoVastuPlan(BaseModel):
    plot_direction: Direction
    plot_width: float = Field(..., gt=0)
    plot_length: float = Field(..., gt=0)
    plot_shape: PlotShape
    main_door_position: Optional[Direction] = None

class VastuRuleEngine:
    def __init__(self, plot_data):
        self.plot_data = plot_data
        self.total_area = plot_data.plot_width * plot_data.plot_length
        self.validation_messages = []
        
        # Room proportions with corridors consideration
        self.ROOM_PROPORTIONS = {
            "living_room": {
                "width_ratio": 0.48,    # Slightly reduced to allow for corridors
                "length_ratio": 0.48
            },
            "master_bedroom": {
                "width_ratio": 0.48,
                "length_ratio": 0.48
            },
            "kitchen": {
                "width_ratio": 0.35,
                "length_ratio": 0.35
            },
            "dining_room": {
                "width_ratio": 0.35,
                "length_ratio": 0.35
            }
        }

    def generate_floor_plan(self) -> List[Dict]:
        """Generate room placements with corridors"""
        width = self.plot_data.plot_width
        length = self.plot_data.plot_length
        
        # Standard measurements
        wall_thickness = 0.23  # 230mm wall thickness
        corridor_width = 1.2   # 1.2m corridor width
        
        # Living Room (top-left)
        living_width = width * self.ROOM_PROPORTIONS["living_room"]["width_ratio"]
        living_length = length * self.ROOM_PROPORTIONS["living_room"]["length_ratio"]
        rooms = [{
            "room_type": "living_room",
            "width": living_width - wall_thickness - corridor_width/2,
            "length": living_length - wall_thickness - corridor_width/2,
            "position_x": 0,
            "position_y": 0,
            "direction": "north"
        }]
        
        # Master Bedroom (top-right)
        master_width = width * self.ROOM_PROPORTIONS["master_bedroom"]["width_ratio"]
        master_length = length * self.ROOM_PROPORTIONS["master_bedroom"]["length_ratio"]
        rooms.append({
            "room_type": "master_bedroom",
            "width": master_width - wall_thickness - corridor_width/2,
            "length": master_length - wall_thickness - corridor_width/2,
            "position_x": living_width + corridor_width,
            "position_y": 0,
            "direction": "south_west"
        })
        
        # Kitchen (bottom-left)
        kitchen_width = width * self.ROOM_PROPORTIONS["kitchen"]["width_ratio"]
        kitchen_length = length * self.ROOM_PROPORTIONS["kitchen"]["length_ratio"]
        rooms.append({
            "room_type": "kitchen",
            "width": kitchen_width - wall_thickness - corridor_width/2,
            "length": kitchen_length - wall_thickness - corridor_width/2,
            "position_x": 0,
            "position_y": living_length + corridor_width,
            "direction": "south_east"
        })
        
        # Dining Room (bottom-right)
        dining_width = width * self.ROOM_PROPORTIONS["dining_room"]["width_ratio"]
        dining_length = length * self.ROOM_PROPORTIONS["dining_room"]["length_ratio"]
        rooms.append({
            "room_type": "dining_room",
            "width": dining_width - wall_thickness - corridor_width/2,
            "length": dining_length - wall_thickness - corridor_width/2,
            "position_x": kitchen_width + corridor_width,
            "position_y": master_length + corridor_width,
            "direction": "west"
        })
        
        return rooms 
    def validate_plot(self) -> bool:
        """Validate plot characteristics according to Vastu"""
        is_valid = True
        
        # Check plot shape requirements
        if self.plot_data.plot_shape == PlotShape.L_SHAPED:
            self.validation_messages.append(
                "L-shaped plots require special consideration. Consider adding a remedy."
            )
            is_valid = False
            
        # Check plot dimensions ratio
        ratio = self.plot_data.plot_width / self.plot_data.plot_length
        if not (0.5 <= ratio <= 2):
            self.validation_messages.append(
                "Plot width to length ratio should be between 1:2 and 2:1"
            )
            is_valid = False
        
        # Check minimum size requirements
        min_area = 30  # minimum 30 square meters
        if self.total_area < min_area:
            self.validation_messages.append(
                f"Plot area {self.total_area:.1f} sq.m is less than minimum required {min_area} sq.m"
            )
            is_valid = False
            
        return is_valid

    def get_validation_messages(self) -> List[str]:
        """Get all validation messages"""
        return self.validation_messages

    def suggest_remedies(self) -> Dict[str, List[str]]:
        """Suggest Vastu remedies for any issues"""
        remedies = {
            "plot_shape": [],
            "room_placement": [],
            "energy_balance": []
        }

        # Add remedies based on validation issues
        if self.plot_data.plot_shape == PlotShape.L_SHAPED:
            remedies["plot_shape"].extend([
                "Place a mirror in the cut portion",
                "Add plants or water features in the cut area",
                "Install proper lighting in the cut portion"
            ])

        # Add room-specific remedies
        for room in self.generate_floor_plan():
            if room["direction"] != Direction.NORTH and room["room_type"] == "living_room":
                remedies["room_placement"].append(
                    "Living room not in ideal north direction. Use light colors and proper lighting."
                )
            elif room["direction"] != Direction.SOUTH_WEST and room["room_type"] == "master_bedroom":
                remedies["room_placement"].append(
                    "Master bedroom not in ideal south-west direction. Consider using earth colors."
                )
            elif room["direction"] != Direction.SOUTH_EAST and room["room_type"] == "kitchen":
                remedies["room_placement"].append(
                    "Kitchen not in ideal south-east direction. Use copper or bronze items."
                )

        # Add general energy balance remedies
        remedies["energy_balance"].extend([
            "Place indoor plants in north-east corner",
            "Install proper ventilation in all rooms",
            "Ensure adequate natural light in all rooms"
        ])

        return remedies
