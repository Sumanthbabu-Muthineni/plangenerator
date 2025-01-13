from PIL import Image, ImageDraw
import numpy as np
from app.models.floor_plan import FloorPlanRequest
import uuid
import os

class FloorPlanGenerator:
    def __init__(self):
        self.output_dir = "generated_plans"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate(self, request: FloorPlanRequest):
        # Calculate pixel dimensions based on scale
        pixels_per_meter = 100  # Adjust as needed
        width_px = int(request.width * pixels_per_meter)
        length_px = int(request.length * pixels_per_meter)

        # Create a new image with white background
        image = Image.new('RGB', (width_px, length_px), 'white')
        draw = ImageDraw.Draw(image)

        # Draw rooms
        for room in request.rooms:
            room_width_px = int(room.width * pixels_per_meter)
            room_length_px = int(room.length * pixels_per_meter)
            x1 = int(room.position_x * pixels_per_meter)
            y1 = int(room.position_y * pixels_per_meter)
            x2 = x1 + room_width_px
            y2 = y1 + room_length_px

            # Draw room outline with pencil effect
            self._draw_pencil_line(draw, [(x1, y1), (x2, y1)])
            self._draw_pencil_line(draw, [(x2, y1), (x2, y2)])
            self._draw_pencil_line(draw, [(x2, y2), (x1, y2)])
            self._draw_pencil_line(draw, [(x1, y2), (x1, y1)])

        # Save the image
        filename = f"{uuid.uuid4()}.png"
        filepath = os.path.join(self.output_dir, filename)
        image.save(filepath)
        
        return filepath

    def _draw_pencil_line(self, draw, points, width=2):
        # Simulate pencil effect by drawing multiple slightly offset lines
        for _ in range(3):
            offset = np.random.randint(-1, 2, size=(2, 2))
            modified_points = [
                (p[0] + o[0], p[1] + o[1])
                for p, o in zip(points, offset)
            ]
            draw.line(modified_points, fill='gray', width=width) 