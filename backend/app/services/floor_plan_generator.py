from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import uuid
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class FloorPlanGenerator:
    def __init__(self, output_dir=None):
        self.pixels_per_meter = 30  # Reduced scale for better fit
        
        # Indian Standard Specifications
        self.STANDARDS = {
            "wall_thickness": 0.23,  # 230mm as per IS 1905
            "door_width": 1.0,       # 1000mm as per NBC
            "door_height": 2.1,      # 2100mm as per NBC
            "window_width": 1.2,     # 1200mm standard
            "window_height": 1.5,    # 1500mm standard
        }

        if output_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            self.output_dir = os.path.join(backend_dir, "generated_plans")
        else:
            self.output_dir = output_dir
            
        os.makedirs(self.output_dir, exist_ok=True)

    def generate(self, plan, room_placements: List[Dict]) -> str:
        try:
            # Calculate dimensions with fixed maximum size
            max_size = 1000  # Increased for more detail
            width_px = int(plan.plot_width * self.pixels_per_meter)
            length_px = int(plan.plot_length * self.pixels_per_meter)
            
            # Scale to fit within max_size while maintaining aspect ratio
            scale = min(max_size / width_px, max_size / length_px)
            width_px = int(width_px * scale)
            length_px = int(length_px * scale)
            self.pixels_per_meter = int(self.pixels_per_meter * scale)

            # Add padding for labels and dimensions
            padding = 100
            image = Image.new('RGB', (width_px + padding * 2, length_px + padding * 2), 'white')
            draw = ImageDraw.Draw(image)

            # Draw base elements
            self._draw_grid(draw, padding, width_px, length_px)
            wall_thickness_px = max(int(self.STANDARDS["wall_thickness"] * self.pixels_per_meter), 4)

            # Draw outer walls with double lines
            outer_wall_thickness = wall_thickness_px * 2
            self._draw_thick_walls(
                draw,
                padding,
                padding,
                width_px,
                length_px,
                outer_wall_thickness
            )
            
            # Process and draw each room with details
            for room in room_placements:
                # Convert room dimensions to pixels
                room_px = {
                    'room_type': room['room_type'],
                    'position_x': int(room['position_x'] * self.pixels_per_meter),
                    'position_y': int(room['position_y'] * self.pixels_per_meter),
                    'width': int(room['width'] * self.pixels_per_meter),
                    'length': int(room['length'] * self.pixels_per_meter),
                    'direction': room.get('direction', 'north')
                }
                
                # Draw detailed room
                self._draw_detailed_room(draw, room_px, padding, wall_thickness_px)
                
                # Draw openings (doors and windows)
                self._draw_room_openings(draw, room_px, padding)
                
                # Add room labels
                self._add_room_labels(draw, [room_px], padding)

            # Add final elements
            self._add_dimensions(draw, padding, width_px, length_px)
            self._add_title_and_scale(draw, width_px + padding * 2, padding)
            self._add_compass(draw, width_px + padding * 2, padding)
            self._add_legend(draw, width_px + padding * 2, length_px + padding)

            # Save high-resolution image
            filename = f"floor_plan_{uuid.uuid4()}.png"
            filepath = os.path.join(self.output_dir, filename)
            image.save(filepath, dpi=(300, 300))
            return filename

        except Exception as e:
            logger.error(f"Error generating floor plan: {str(e)}", exc_info=True)
            raise
        
    def _draw_grid(self, draw, padding, width, length):
        """Draw lighter grid"""
        grid_color = '#EEEEEE'  # Very light gray
        
        # Vertical lines
        for x in range(0, width + 1, self.pixels_per_meter):
            draw.line(
                [x + padding, padding, x + padding, length + padding],
                fill=grid_color,
                width=1
            )

        # Horizontal lines
        for y in range(0, length + 1, self.pixels_per_meter):
            draw.line(
                [padding, y + padding, width + padding, y + padding],
                fill=grid_color,
                width=1
            )

    def _draw_walls(self, draw, padding, width, length, wall_thickness, color):
        """Draw walls with specified color"""
        # Draw as filled rectangle for consistent thickness
        draw.rectangle(
            [padding, padding, width + padding, length + padding],
            outline=color,
            width=wall_thickness
        )

    def _draw_rooms(self, draw, room_placements, padding, wall_thickness):
        """Draw rooms with internal walls"""
        for room in room_placements:
            x = int(room['position_x'] * self.pixels_per_meter) + padding
            y = int(room['position_y'] * self.pixels_per_meter) + padding
            w = int(room['width'] * self.pixels_per_meter)
            l = int(room['length'] * self.pixels_per_meter)

            # Draw room walls in dark gray
            draw.rectangle(
                [x, y, x + w, y + l],
                outline='#404040',
                width=max(wall_thickness - 1, 1)
            )

    def _draw_door(self, draw, x, y, direction, is_main_door=False):
        """Draw door with proper architectural symbol"""
        door_width_px = int(self.STANDARDS["door_width"] * self.pixels_per_meter)
        arc_radius = door_width_px
        
        if direction in ['north', 'south']:
            # Draw door frame
            draw.line([x, y, x + door_width_px, y], fill='black', width=2)
            
            # Draw door swing arc
            if direction == 'north':
                draw.arc([x, y, x + arc_radius, y + arc_radius], 0, 90, fill='black', width=1)
            else:
                draw.arc([x, y - arc_radius, x + arc_radius, y], 270, 360, fill='black', width=1)
                
            # Add door symbol
            if is_main_door:
                draw.line([x, y - 5, x + door_width_px, y - 5], fill='black', width=2)
                
        else:  # east or west
            # Draw door frame
            draw.line([x, y, x, y + door_width_px], fill='black', width=2)
            
            # Draw door swing arc
            if direction == 'east':
                draw.arc([x, y, x + arc_radius, y + arc_radius], 90, 180, fill='black', width=1)
            else:
                draw.arc([x - arc_radius, y, x, y + arc_radius], 270, 360, fill='black', width=1)
                
            # Add main door symbol
            if is_main_door:
                draw.line([x - 5, y, x - 5, y + door_width_px], fill='black', width=2)
    def _draw_detailed_room(self, draw, room, padding, wall_thickness):
        """Draw room with detailed architectural elements"""
        x = int(room['position_x']) + padding
        y = int(room['position_y']) + padding
        w = int(room['width'])
        l = int(room['length'])
        room_type = room['room_type'].lower()

        # Draw room walls with proper thickness
        self._draw_thick_walls(draw, x, y, w, l, wall_thickness)
        
        # Add room-specific elements based on type
        if 'kitchen' in room_type:
            self._draw_kitchen_elements(draw, x, y, w, l)
        elif 'bedroom' in room_type:
            self._draw_bedroom_elements(draw, x, y, w, l)
        elif 'bathroom' in room_type:
            self._draw_bathroom_elements(draw, x, y, w, l)
        elif 'living' in room_type:
            self._draw_living_room_elements(draw, x, y, w, l)
        elif 'dining' in room_type:
            self._draw_dining_room_elements(draw, x, y, w, l)
    def _draw_dining_room_elements(self, draw, x, y, width, length):
        """Draw dining room furniture"""
        # Dining table
        table_width = int(1.8 * self.pixels_per_meter)  # 180cm table
        table_length = int(1.0 * self.pixels_per_meter)  # 100cm length
        
        # Center the table in the room
        table_x = x + (width - table_width) // 2
        table_y = y + (length - table_length) // 2
        
        # Draw table
        draw.rectangle(
            [table_x, table_y, table_x + table_width, table_y + table_length],
            outline='black',
            width=2
        )
        
        # Draw chairs (6 chairs)
        chair_size = int(0.4 * self.pixels_per_meter)
        chair_positions = [
            # Left side chairs
            (table_x - chair_size, table_y - chair_size//2),
            (table_x - chair_size, table_y + table_length//2 - chair_size//2),
            # Right side chairs
            (table_x + table_width, table_y - chair_size//2),
            (table_x + table_width, table_y + table_length//2 - chair_size//2),
            # End chairs
            (table_x + table_width//2 - chair_size//2, table_y - chair_size),
            (table_x + table_width//2 - chair_size//2, table_y + table_length)
        ]
        
        for chair_x, chair_y in chair_positions:
            draw.rectangle(
                [chair_x, chair_y, chair_x + chair_size, chair_y + chair_size],
                outline='black',
                width=1
            )
    
    def _draw_bathroom_elements(self, draw, x, y, width, length):
        """Draw bathroom fixtures"""
        # Toilet
        toilet_width = int(0.7 * self.pixels_per_meter)  # 70cm toilet unit
        toilet_depth = int(0.7 * self.pixels_per_meter)
        draw.ellipse([x + 10, y + 10, x + toilet_width, y + toilet_depth],
                    outline='black', width=1)
        
        # Sink
        sink_width = int(0.6 * self.pixels_per_meter)
        sink_x = x + width - sink_width - 10
        draw.rectangle([sink_x, y + 10, sink_x + sink_width, y + sink_width],
                      outline='black', width=1)
        # Sink basin
        draw.arc([sink_x + 5, y + 15, sink_x + sink_width - 5, y + sink_width - 5],
                 0, 360, fill='black', width=1)

        # Shower area or bathtub
        shower_width = int(1.2 * self.pixels_per_meter)
        draw.rectangle(
            [x + width - shower_width - 10, y + length - shower_width - 10,
             x + width - 10, y + length - 10],
            outline='black',
            width=1
        )
    def _draw_bedroom_elements(self, draw, x, y, width, length):
        """Draw bedroom furniture"""
        # Bed
        bed_width = int(1.8 * self.pixels_per_meter)  # 180cm bed width
        bed_length = int(2.0 * self.pixels_per_meter)  # 200cm bed length
        bed_x = x + (width - bed_width) // 2
        bed_y = y + (length - bed_length) // 2
        
        draw.rectangle([bed_x, bed_y, bed_x + bed_width, bed_y + bed_length],
                      outline='black', width=1)
        # Pillow area
        pillow_height = int(0.4 * self.pixels_per_meter)
        draw.rectangle([bed_x, bed_y, bed_x + bed_width, bed_y + pillow_height],
                      outline='black', width=1)

        # Wardrobe
        wardrobe_depth = int(0.6 * self.pixels_per_meter)
        draw.rectangle([x + 10, y + 10, x + width - 10, y + wardrobe_depth],
                      outline='black', width=1)
    def _draw_living_room_elements(self, draw, x, y, width, length):
        """Draw living room furniture"""
        # Sofa
        sofa_depth = int(0.9 * self.pixels_per_meter)
        sofa_width = int(2.4 * self.pixels_per_meter)
        draw.rectangle([x + 10, y + length - sofa_depth - 10,
                       x + sofa_width, y + length - 10],
                      outline='black', width=1)
        
        # Coffee table
        table_size = int(1.0 * self.pixels_per_meter)
        table_x = x + sofa_width + 20
        table_y = y + length - sofa_depth - 5
        draw.rectangle([table_x, table_y,
                       table_x + table_size, table_y + table_size],
                      outline='black', width=1)
    def _draw_kitchen_elements(self, draw, x, y, width, length):
        """Draw detailed kitchen fixtures"""
        counter_depth = int(0.6 * self.pixels_per_meter)  # 60cm counter depth
        
        # L-shaped counter
        draw.line([x + 10, y + 10, x + width - 10, y + 10], fill='black', width=2)  # Top counter
        draw.line([x + width - counter_depth - 10, y + 10, x + width - counter_depth - 10, y + length - 10], 
                 fill='black', width=2)  # Side counter
        
        # Sink
        sink_width = int(0.9 * self.pixels_per_meter)
        sink_x = x + width - counter_depth - sink_width - 20
        sink_y = y + 20
        self._draw_sink(draw, sink_x, sink_y, sink_width, counter_depth)
        
        # Stove/Cooktop
        stove_width = int(0.6 * self.pixels_per_meter)
        stove_x = x + width - counter_depth - 20
        stove_y = y + length//2
        self._draw_stove(draw, stove_x, stove_y, stove_width, counter_depth)
        
        # Refrigerator
        fridge_width = int(0.8 * self.pixels_per_meter)
        fridge_depth = int(0.7 * self.pixels_per_meter)
        draw.rectangle(
            [x + 20, y + length - fridge_depth - 20,
             x + 20 + fridge_width, y + length - 20],
            outline='black',
            width=2
        )
    def _draw_sink(self, draw, x, y, width, depth):
        """Draw detailed kitchen sink"""
        # Draw sink counter
        draw.rectangle(
            [x, y, x + width, y + depth],
            outline='black',
            width=1
        )
        
        # Draw double sink basins
        basin_width = (width - 20) // 2
        # Left basin
        draw.rectangle(
            [x + 5, y + 5, x + basin_width, y + depth - 5],
            outline='black',
            width=1
        )
        # Right basin
        draw.rectangle(
            [x + width - basin_width - 5, y + 5, x + width - 5, y + depth - 5],
            outline='black',
            width=1
        )
        
        # Draw sink drains (circles)
        drain_radius = 3
        # Left drain
        center_x1 = x + basin_width // 2
        center_y1 = y + depth // 2
        draw.ellipse(
            [center_x1 - drain_radius, center_y1 - drain_radius,
             center_x1 + drain_radius, center_y1 + drain_radius],
            fill='black'
        )
        # Right drain
        center_x2 = x + width - basin_width // 2
        center_y2 = y + depth // 2
        draw.ellipse(
            [center_x2 - drain_radius, center_y2 - drain_radius,
             center_x2 + drain_radius, center_y2 + drain_radius],
            fill='black'
        )
        
        # Draw faucet
        faucet_x = x + width // 2
        faucet_y = y + 2
        # Faucet base
        draw.rectangle(
            [faucet_x - 5, faucet_y, faucet_x + 5, faucet_y + 5],
            outline='black',
            width=1
        )
        # Faucet spout
        draw.arc(
            [faucet_x - 10, faucet_y - 10, faucet_x + 10, faucet_y + 10],
            180, 270,
            fill='black',
            width=1
        )
    def _draw_stove(self, draw, x, y, width, depth):
        """Draw detailed stove/cooktop"""
        draw.rectangle([x, y, x + width, y + depth], outline='black', width=1)
        # Draw burners
        burner_size = width // 4
        for i in range(4):
            bx = x + (i % 2) * (width//2) + burner_size//2
            by = y + (i // 2) * (depth//2) + burner_size//2
            draw.ellipse([bx, by, bx + burner_size, by + burner_size],
                        outline='black', width=1)

    
    def _draw_thick_walls(self, draw, x, y, width, length, thickness):
        """Draw walls with proper thickness"""
        # Outer walls
        draw.rectangle([x, y, x + width, y + length], outline='black', width=thickness)
        # Inner wall fill
        draw.rectangle(
            [x + thickness//2, y + thickness//2, 
             x + width - thickness//2, y + length - thickness//2],
            outline='black',
            width=1
        )

    def _draw_window(self, draw, x, y, direction):
        """Draw detailed window with frame and sill"""
        window_width_px = int(self.STANDARDS["window_width"] * self.pixels_per_meter)
        window_height_px = int(0.3 * self.pixels_per_meter)  # Window frame height

        if direction in ['north', 'south']:
            # Window frame
            draw.rectangle([x, y, x + window_width_px, y + window_height_px],
                         outline='black', width=1)
            # Window panes
            pane_width = window_width_px // 3
            for i in range(1, 3):
                draw.line([x + i * pane_width, y,
                          x + i * pane_width, y + window_height_px],
                         fill='black', width=1)
            # Window sill
            draw.line([x - 5, y + window_height_px,
                      x + window_width_px + 5, y + window_height_px],
                     fill='black', width=2)
        else:
            # Vertical window
            draw.rectangle([x, y, x + window_height_px, y + window_width_px],
                         outline='black', width=1)
            # Window panes
            pane_height = window_width_px // 3
            for i in range(1, 3):
                draw.line([x, y + i * pane_height,
                          x + window_height_px, y + i * pane_height],
                         fill='black', width=1)
            # Window sill
            draw.line([x + window_height_px, y - 5,
                      x + window_height_px, y + window_width_px + 5],
                     fill='black', width=2)

    def _draw_room_openings(self, draw, room, padding):
        """Draw doors and windows for each room"""
        x = int(room['position_x'] * self.pixels_per_meter) + padding
        y = int(room['position_y'] * self.pixels_per_meter) + padding
        width = int(room['width'] * self.pixels_per_meter)
        length = int(room['length'] * self.pixels_per_meter)
        room_type = room['room_type']

        # Get door and window positions based on room type
        door_positions = self._get_door_positions(room_type, x, y, width, length)
        window_positions = self._get_window_positions(room_type, x, y, width, length)

        # Draw doors
        for dp in door_positions:
            self._draw_door(draw, dp[0], dp[1], dp[2], dp[3])
        
        # Draw windows
        for wp in window_positions:
            self._draw_window(draw, wp[0], wp[1], wp[2])


    def _get_door_positions(self, room_type, x, y, width, length):
        """Get door positions based on room type and Vastu principles"""
        positions = []
        
        if room_type == "living_room":
            # Main entrance on east or north wall
            positions.append((int(x + width // 4), int(y), 'north', True))
        
        elif room_type == "bedroom":
            # Door on east or north wall
            positions.append((int(x + width // 3), int(y), 'north', False))
        
        elif room_type == "kitchen":
            # Door on east wall
            positions.append((int(x + width), int(y + length // 2), 'east', False))
        
        elif room_type == "bathroom":
            # Door on west wall
            positions.append((int(x), int(y + length // 3), 'west', False))
        
        return positions

    def _get_window_positions(self, room_type, x, y, width, length):
        """Get window positions based on room type and ventilation needs"""
        positions = []
        
        if room_type == "living_room":
            # Windows on north and east walls
            positions.extend([
                (int(x + width // 3), int(y), 'north'),
                (int(x + 2 * width // 3), int(y), 'north'),
                (int(x + width), int(y + length // 2), 'east')
            ])
        
        elif room_type == "bedroom":
            # Windows on north and east/west walls
            positions.extend([
                (int(x + width // 2), int(y), 'north'),
                (int(x + width), int(y + length // 2), 'east')
            ])
        
        elif room_type == "kitchen":
            # Windows on east and north/south walls
            positions.extend([
                (int(x + width), int(y + length // 3), 'east'),
                (int(x + width // 2), int(y), 'north')
            ])
        
        return positions


    def _add_room_labels(self, draw, room_placements, padding):
        """Add room labels with measurements"""
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
            'C:\\Windows\\Fonts\\arial.ttf',
        ]

        font = None
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, 12)  # Smaller font size
                break
            except (OSError, IOError):
                continue

        if font is None:
            font = ImageFont.load_default()

        for room in room_placements:
            x = int(room['position_x']) + padding
            y = int(room['position_y']) + padding
            w = int(room['width'])
            l = int(room['length'])

            # Room name
            label = f"{room['room_type'].replace('_', ' ').title()}"
            # Room dimensions with proper units
            dims = f"{room['width']:.1f}m × {room['length']:.1f}m"

            # Calculate text positions
            if hasattr(draw, 'textlength'):
                text_width = int(draw.textlength(label, font=font))
            else:
                text_width = len(label) * 6  # Approximate width

            # Center text in room
            text_x = x + (w - text_width) // 2
            text_y = y + l // 3  # Move text higher in the room

            # Draw labels with white background
            self._draw_text_with_background(draw, text_x, text_y, label, font)
            
            # Draw dimensions below room name
            if hasattr(draw, 'textlength'):
                dims_width = int(draw.textlength(dims, font=font))
            else:
                dims_width = len(dims) * 6

            dims_x = x + (w - dims_width) // 2
            dims_y = text_y + 20  # Space below room name
            self._draw_text_with_background(draw, dims_x, dims_y, dims, font)
    def _draw_text_with_background(self, draw, x, y, text, font):
        """Helper method to draw text with white background"""
        # Get text size
        if hasattr(font, 'getbbox'):
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            text_width = len(text) * 6
            text_height = 12

        # Draw white background
        padding = 2
        draw.rectangle(
            [x - padding, y - padding,
             x + text_width + padding, y + text_height + padding],
            fill='white'
        )
        draw.text((x, y), text, fill='black', font=font)


    def _add_title_and_scale(self, draw, width, padding):
        """Add title and scale information with better font handling"""
        # Try to load a larger font for title
        font = None
        small_font = None
        
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
            '/System/Library/Fonts/Helvetica.ttf',
            'C:\\Windows\\Fonts\\arial.ttf',
        ]

        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, 16)
                small_font = ImageFont.truetype(font_path, 12)
                break
            except (OSError, IOError):
                continue

        if font is None:
            font = ImageFont.load_default()
            small_font = font

        # Add title
        title = "Floor Plan (as per NBC & Vastu)"
        draw.text((padding, padding//2), title, fill='black', font=font)

        # Add scale
        scale_text = f"Scale 1:{int(100/self.pixels_per_meter)}"
        draw.text((width - 150, padding//2), scale_text, fill='black', font=small_font)
    def _add_dimensions(self, draw, padding, width, length):
        """Add dimension lines and measurements"""
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()

        # Draw dimension lines with arrows
        arrow_size = 5
        offset = 30

        # Width dimension
        draw.line([padding, padding - offset, width + padding, padding - offset], fill='black', width=1)
        draw.line([padding, padding - offset - arrow_size, padding, padding - offset + arrow_size], fill='black', width=1)
        draw.line([width + padding, padding - offset - arrow_size, width + padding, padding - offset + arrow_size], fill='black', width=1)

        # Length dimension
        draw.line([padding - offset, padding, padding - offset, length + padding], fill='black', width=1)
        draw.line([padding - offset - arrow_size, padding, padding - offset + arrow_size, padding], fill='black', width=1)
        draw.line([padding - offset - arrow_size, length + padding, padding - offset + arrow_size, length + padding], fill='black', width=1)

        # Add measurements
        draw.text((padding + width//2 - 20, padding - offset - 20), f"{width/self.pixels_per_meter:.1f}m", fill='black', font=font)
        draw.text((padding - offset - 40, padding + length//2 - 10), f"{length/self.pixels_per_meter:.1f}m", fill='black', font=font)


    def _add_compass(self, draw, width, padding):
        """Add compass rose to indicate directions"""
        center_x = width - 60
        center_y = padding + 60
        radius = 20

        # Draw circle
        draw.ellipse(
            [center_x - radius, center_y - radius,
             center_x + radius, center_y + radius],
            outline='black'
        )

        # Draw direction arrows
        directions = ['N', 'E', 'S', 'W']
        positions = [
            (0, -radius - 10),  # North
            (radius + 10, 0),   # East
            (0, radius + 10),   # South
            (-radius - 10, 0)   # West
        ]

        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()

        for direction, pos in zip(directions, positions):
            draw.text(
                (center_x + pos[0], center_y + pos[1]),
                direction,
                fill='black',
                font=font,
                anchor="mm"
            )

    def _add_legend(self, draw, width, height):
        """Add legend with specifications at bottom-right"""
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()

        # Move legend to bottom-right corner, inside the plan area
        legend_start_x = width - 180
        legend_start_y = height - 100
        line_height = 15

        # Draw legend box with thinner border
        draw.rectangle(
            [legend_start_x - 5, legend_start_y - 5,
             legend_start_x + 145, legend_start_y + 75],
            outline='black',
            width=1
        )

        # Add legend items with more compact layout
        legend_items = [
            "Wall Thickness: 230mm",
            "Door Width: 1.0m",
            "Window Size: 1.2×1.5m",
            "Room Height: 3.0m",
            f"Scale 1:{int(100/self.pixels_per_meter)}"
        ]

        for i, item in enumerate(legend_items):
            draw.text(
                (legend_start_x, legend_start_y + i * line_height),
                item,
                fill='black',
                font=font
            )
