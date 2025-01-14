import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './FloorPlanResults.css';

const FloorPlanResults = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [imageUrl, setImageUrl] = useState(null);

  const { floorPlan } = location.state || {};

  useEffect(() => {
    if (floorPlan?.plan_details?.plan_image_url) {
      const url = `http://localhost:8000${floorPlan.plan_details.plan_image_url}`;
      console.log('Attempting to load image from:', url);
      setImageUrl(url);
    }
  }, [floorPlan]);

  if (!floorPlan) {
    return (
      <div className="results-container">
        <div className="error-message">
          No floor plan data available. Please generate a new plan.
        </div>
        <button onClick={() => navigate('/')} className="back-button">
          Back to Form
        </button>
      </div>
    );
  }

  const {
    plan_details: {
      plot_width,
      plot_length,
      direction,
      shape,
      main_door,
      room_placements = [],
      validation_messages = [],
      remedies = {}
    }
  } = floorPlan;

  return (
    <div className="results-container">
      <h1 className="results-title">Your Vastu-Compliant Floor Plan</h1>

      {/* Floor Plan Image */}
      <div className="floor-plan-image">
        <h2>Floor Plan Visualization</h2>
        {loading && <div className="loading">Loading floor plan...</div>}
        {error && <div className="error-message">{error}</div>}
        {imageUrl && (
          <img
            src={imageUrl}
            alt="Generated Floor Plan"
            onLoad={() => setLoading(false)}
            onError={(e) => {
              console.error('Error loading image:', e);
              setError('Failed to load floor plan image');
              setLoading(false);
            }}
            style={{ display: loading ? 'none' : 'block' }}
          />
        )}
      </div>

      {/* Plot Details */}
      <div className="plot-details">
        <h2>Plot Details</h2>
        <div className="details-grid">
          <div><strong>Width:</strong> {plot_width} meters</div>
          <div><strong>Length:</strong> {plot_length} meters</div>
          <div><strong>Direction:</strong> {direction}</div>
          <div><strong>Shape:</strong> {shape}</div>
          <div><strong>Main Door:</strong> {main_door}</div>
        </div>
      </div>

      {/* Room Placements */}
      {room_placements.length > 0 && (
        <div className="room-placements">
          <h2>Room Placements</h2>
          <div className="rooms-grid">
            {room_placements.map((room, index) => (
              <div key={index} className="room-card">
                <h3>{room.room_type.replace('_', ' ').toUpperCase()}</h3>
                <p>Direction: {room.direction}</p>
                <p>Size: {room.width}m × {room.length}m</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Navigation */}
      <button onClick={() => navigate('/')} className="back-button">
        Generate Another Plan
      </button>
    </div>
  );
};

export default FloorPlanResults;