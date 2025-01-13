import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './FloorPlanGenerator.css';

const FloorPlanGenerator = () => {
  const navigate = useNavigate();
  const [floorPlan, setFloorPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    width: 10,
    length: 15,
    scale: 1.0,
    rooms: [{
      width: 4,
      length: 5,
      position_x: 0,
      position_y: 0,
      room_type: "living_room"
    }],
    style: "pencil"
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: parseFloat(value) || value
    }));
  };

  const handleRoomChange = (index, field, value) => {
    setFormData(prev => {
      const updatedRooms = [...prev.rooms];
      updatedRooms[index] = {
        ...updatedRooms[index],
        [field]: parseFloat(value) || value
      };
      return {
        ...prev,
        rooms: updatedRooms
      };
    });
  };

  const addRoom = () => {
    setFormData(prev => ({
      ...prev,
      rooms: [...prev.rooms, {
        width: 4,
        length: 5,
        position_x: 0,
        position_y: 0,
        room_type: "bedroom"
      }]
    }));
  };

  const removeRoom = (index) => {
    setFormData(prev => ({
      ...prev,
      rooms: prev.rooms.filter((_, i) => i !== index)
    }));
  };

  const generateFloorPlan = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      navigate('/results', { state: formData });
    } catch (error) {
      console.error('Error:', error);
      setLoading(false);
    }
  };

  return (
    <div className="floor-plan-container">
      <form onSubmit={generateFloorPlan} className="floor-plan-form">
        <div className="form-group">
          <h2>Floor Plan Dimensions</h2>
          <div className="input-group">
            <label>
              Width (meters):
              <input
                type="number"
                name="width"
                value={formData.width}
                onChange={handleInputChange}
                min="1"
                step="0.1"
                required
              />
            </label>
          </div>
          <div className="input-group">
            <label>
              Length (meters):
              <input
                type="number"
                name="length"
                value={formData.length}
                onChange={handleInputChange}
                min="1"
                step="0.1"
                required
              />
            </label>
          </div>
          <div className="input-group">
            <label>
              Scale:
              <input
                type="number"
                name="scale"
                value={formData.scale}
                onChange={handleInputChange}
                min="0.1"
                step="0.1"
                required
              />
            </label>
          </div>
        </div>

        <div className="form-group">
          <h2>Rooms</h2>
          {formData.rooms.map((room, index) => (
            <div key={index} className="room-inputs">
              <h3>Room {index + 1}</h3>
              <div className="input-group">
                <label>
                  Type:
                  <select
                    value={room.room_type}
                    onChange={(e) => handleRoomChange(index, 'room_type', e.target.value)}
                  >
                    <option value="living_room">Living Room</option>
                    <option value="bedroom">Bedroom</option>
                    <option value="kitchen">Kitchen</option>
                    <option value="bathroom">Bathroom</option>
                  </select>
                </label>
              </div>
              <div className="input-group">
                <label>
                  Width:
                  <input
                    type="number"
                    value={room.width}
                    onChange={(e) => handleRoomChange(index, 'width', e.target.value)}
                    min="1"
                    step="0.1"
                    required
                  />
                </label>
              </div>
              <div className="input-group">
                <label>
                  Length:
                  <input
                    type="number"
                    value={room.length}
                    onChange={(e) => handleRoomChange(index, 'length', e.target.value)}
                    min="1"
                    step="0.1"
                    required
                  />
                </label>
              </div>
              <div className="input-group">
                <label>
                  Position X:
                  <input
                    type="number"
                    value={room.position_x}
                    onChange={(e) => handleRoomChange(index, 'position_x', e.target.value)}
                    step="0.1"
                    required
                  />
                </label>
              </div>
              <div className="input-group">
                <label>
                  Position Y:
                  <input
                    type="number"
                    value={room.position_y}
                    onChange={(e) => handleRoomChange(index, 'position_y', e.target.value)}
                    step="0.1"
                    required
                  />
                </label>
              </div>
              <button 
                type="button" 
                onClick={() => removeRoom(index)}
                className="remove-room-btn"
              >
                Remove Room
              </button>
            </div>
          ))}
          <button 
            type="button" 
            onClick={addRoom}
            className="add-room-btn"
          >
            Add Room
          </button>
        </div>

        <button 
          type="submit" 
          disabled={loading}
          className="generate-btn"
        >
          {loading ? 'Generating...' : 'Generate Floor Plan'}
        </button>
      </form>

      {floorPlan && (
        <div className="floor-plan-result">
          <h2>Generated Floor Plan</h2>
          <img src={floorPlan} alt="Generated Floor Plan" />
        </div>
      )}
    </div>
  );
};

export default FloorPlanGenerator; 