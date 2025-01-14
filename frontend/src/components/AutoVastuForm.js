import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './AutoVastuForm.css';

const AutoVastuForm = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    plot_direction: 'north',
    plot_width: '',
    plot_length: '',
    plot_shape: 'rectangular',
    main_door_position: 'east'
  });

  const directions = [
    { value: 'north', label: 'North' },
    { value: 'south', label: 'South' },
    { value: 'east', label: 'East' },
    { value: 'west', label: 'West' },
    { value: 'north_east', label: 'North East' },
    { value: 'north_west', label: 'North West' },
    { value: 'south_east', label: 'South East' },
    { value: 'south_west', label: 'South West' }
  ];

  const plotShapes = [
    { value: 'rectangular', label: 'Rectangular' },
    { value: 'square', label: 'Square' },
    { value: 'l_shaped', label: 'L-Shaped' }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name.includes('plot_') && !name.includes('direction') && !name.includes('shape') 
        ? parseFloat(value) 
        : value
    }));
  };

  const validateForm = () => {
    const errors = [];
    if (!formData.plot_width || formData.plot_width <= 0) {
      errors.push('Plot width must be greater than 0');
    }
    if (!formData.plot_length || formData.plot_length <= 0) {
      errors.push('Plot length must be greater than 0');
    }
    return errors;
  };
  
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    // Format and validate data
    const requestData = {
      plot_direction: formData.plot_direction,
      plot_width: Number(formData.plot_width),  // Ensure numeric conversion
      plot_length: Number(formData.plot_length), // Ensure numeric conversion
      plot_shape: formData.plot_shape,
      main_door_position: formData.main_door_position
    };

    // Validate numbers
    if (isNaN(requestData.plot_width) || isNaN(requestData.plot_length)) {
      setError('Please enter valid numbers for width and length');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/api/generate-floor-plan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate floor plan');
      }

      const data = await response.json();
      navigate('/results', { 
        state: { 
          floorPlan: data,
          originalInput: requestData 
        } 
      });
    } catch (err) {
      console.error('Error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="vastu-form-container">
      <div className="form-card">
        <h1 className="form-title">Vastu Floor Plan Generator</h1>
        <p className="form-subtitle">Enter your plot details to generate a Vastu-compliant floor plan</p>
        
        <form onSubmit={handleSubmit} className="form-content">
          {/* Plot Direction */}
          <div className="form-group">
            <label>Plot Direction</label>
            <select
              name="plot_direction"
              value={formData.plot_direction}
              onChange={handleInputChange}
              className="form-select"
            >
              {directions.map((direction) => (
                <option key={direction.value} value={direction.value}>
                  {direction.label}
                </option>
              ))}
            </select>
          </div>

          {/* Plot Shape */}
          <div className="form-group">
            <label>Plot Shape</label>
            <select
              name="plot_shape"
              value={formData.plot_shape}
              onChange={handleInputChange}
              className="form-select"
            >
              {plotShapes.map((shape) => (
                <option key={shape.value} value={shape.value}>
                  {shape.label}
                </option>
              ))}
            </select>
          </div>

          {/* Plot Dimensions */}
          <div className="form-row">
            <div className="form-group">
              <label>Width (meters)</label>
              <input
                type="number"
                name="plot_width"
                value={formData.plot_width}
                onChange={handleInputChange}
                min="1"
                step="0.1"
                placeholder="Enter width"
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Length (meters)</label>
              <input
                type="number"
                name="plot_length"
                value={formData.plot_length}
                onChange={handleInputChange}
                min="1"
                step="0.1"
                placeholder="Enter length"
                className="form-input"
              />
            </div>
          </div>

          {/* Main Door Position */}
          <div className="form-group">
            <label>Main Door Position</label>
            <select
              name="main_door_position"
              value={formData.main_door_position}
              onChange={handleInputChange}
              className="form-select"
            >
              {directions.map((direction) => (
                <option key={direction.value} value={direction.value}>
                  {direction.label}
                </option>
              ))}
            </select>
          </div>

          {/* Error Display */}
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            className="submit-button"
            disabled={loading}
          >
            {loading ? 'Generating Floor Plan...' : 'Generate Floor Plan'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default AutoVastuForm;