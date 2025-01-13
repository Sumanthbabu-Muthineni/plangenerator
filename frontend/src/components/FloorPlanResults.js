import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';

function FloorPlanResults() {
  const [loading, setLoading] = useState(true);
  const [floorPlans, setFloorPlans] = useState(null);
  const [error, setError] = useState(null);
  const location = useLocation();
  const formData = location.state;

  useEffect(() => {
    const generateFloorPlans = async () => {
      try {
        const response = await axios.post(
          'http://localhost:8000/api/generate-floor-plan',
          formData,
          {
            headers: {
              'Content-Type': 'application/json',
            },
          }
        );
        setFloorPlans(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error generating floor plans:', error);
        setError('Failed to generate floor plans');
        setLoading(false);
      }
    };

    if (formData) {
      generateFloorPlans();
    }
  }, [formData]);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loader"></div>
        <p>Generating your Vastu-compliant floor plans...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="floor-plans-container">
      <h2>Your Vastu-Compliant Floor Plans</h2>
      {floorPlans && floorPlans.image_url && (
        <div className="plans-grid">
          <div className="plan-item">
            <h3>Generated Floor Plan</h3>
            <img src={floorPlans.image_url} alt="Generated Floor Plan" />
          </div>
        </div>
      )}
    </div>
  );
}

export default FloorPlanResults; 