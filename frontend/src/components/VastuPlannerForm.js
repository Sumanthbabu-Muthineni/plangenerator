import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const VastuPlannerForm = () => {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    plotLength: '',
    plotWidth: '',
    plotDirection: '',
    mainDoor: '',
    kitchenPreference: '',
    poojaRoom: '',
    bedrooms: '',
    parking: false
  });

  const [errors, setErrors] = useState({});

  const directions = ['North', 'South', 'East', 'West', 'North-East', 'North-West', 'South-East', 'South-West'];
  
  const vastuRules = {
    mainDoor: {
      'North': 'Highly favorable',
      'East': 'Most favorable',
      'South': 'Avoid if possible',
      'West': 'Moderately favorable'
    },
    kitchen: {
      'South-East': 'Most favorable',
      'North-West': 'Avoid',
      'East': 'Favorable'
    },
    poojaRoom: {
      'North-East': 'Most favorable',
      'East': 'Favorable'
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.plotLength || !formData.plotWidth) {
      newErrors.plot = 'Plot dimensions are required';
    }
    
    if (!formData.plotDirection) {
      newErrors.direction = 'Plot direction is required';
    }
    
    if (formData.mainDoor === 'South' && formData.plotDirection === 'South') {
      newErrors.vastuConflict = 'South-facing main door for south-facing plot is not recommended';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      const formData = {
        // ... your form data
      };

      navigate('/results', { state: formData });
    }
  };

  const formStyles = {
    container: {
      maxWidth: '600px',
      margin: '0 auto',
      padding: '20px',
      fontFamily: 'Arial, sans-serif'
    },
    section: {
      marginBottom: '20px'
    },
    heading: {
      fontSize: '1.2rem',
      fontWeight: 'bold',
      marginBottom: '10px'
    },
    inputGroup: {
      marginBottom: '15px'
    },
    label: {
      display: 'block',
      marginBottom: '5px',
      fontSize: '0.9rem'
    },
    input: {
      width: '100%',
      padding: '8px',
      border: '1px solid #ccc',
      borderRadius: '4px'
    },
    select: {
      width: '100%',
      padding: '8px',
      border: '1px solid #ccc',
      borderRadius: '4px'
    },
    error: {
      color: 'red',
      fontSize: '0.8rem',
      marginTop: '5px'
    },
    button: {
      backgroundColor: '#007bff',
      color: 'white',
      padding: '10px 20px',
      border: 'none',
      borderRadius: '4px',
      cursor: 'pointer',
      width: '100%'
    }
  };

  return (
    <div style={formStyles.container}>
      <h2 style={{ fontSize: '1.5rem', marginBottom: '20px' }}>Vastu Floor Plan Generator</h2>
      
      <form onSubmit={handleSubmit}>
        {/* Plot Details */}
        <div style={formStyles.section}>
          <h3 style={formStyles.heading}>Plot Details</h3>
          
          <div style={formStyles.inputGroup}>
            <label style={formStyles.label}>Plot Length (feet)</label>
            <input
              type="number"
              name="plotLength"
              value={formData.plotLength}
              onChange={handleInputChange}
              style={formStyles.input}
            />
          </div>

          <div style={formStyles.inputGroup}>
            <label style={formStyles.label}>Plot Width (feet)</label>
            <input
              type="number"
              name="plotWidth"
              value={formData.plotWidth}
              onChange={handleInputChange}
              style={formStyles.input}
            />
          </div>

          <div style={formStyles.inputGroup}>
            <label style={formStyles.label}>Plot Direction</label>
            <select
              name="plotDirection"
              value={formData.plotDirection}
              onChange={handleInputChange}
              style={formStyles.select}
            >
              <option value="">Select Direction</option>
              {directions.map(dir => (
                <option key={dir} value={dir}>{dir}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Vastu Preferences */}
        <div style={formStyles.section}>
          <h3 style={formStyles.heading}>Vastu Preferences</h3>
          
          <div style={formStyles.inputGroup}>
            <label style={formStyles.label}>Main Door Direction</label>
            <select
              name="mainDoor"
              value={formData.mainDoor}
              onChange={handleInputChange}
              style={formStyles.select}
            >
              <option value="">Select Direction</option>
              {directions.map(dir => (
                <option key={dir} value={dir}>
                  {dir} {vastuRules.mainDoor[dir] ? `(${vastuRules.mainDoor[dir]})` : ''}
                </option>
              ))}
            </select>
          </div>

          <div style={formStyles.inputGroup}>
            <label style={formStyles.label}>Kitchen Placement</label>
            <select
              name="kitchenPreference"
              value={formData.kitchenPreference}
              onChange={handleInputChange}
              style={formStyles.select}
            >
              <option value="">Select Direction</option>
              {directions.map(dir => (
                <option key={dir} value={dir}>
                  {dir} {vastuRules.kitchen[dir] ? `(${vastuRules.kitchen[dir]})` : ''}
                </option>
              ))}
            </select>
          </div>

          <div style={formStyles.inputGroup}>
            <label style={formStyles.label}>Pooja Room Placement</label>
            <select
              name="poojaRoom"
              value={formData.poojaRoom}
              onChange={handleInputChange}
              style={formStyles.select}
            >
              <option value="">Select Direction</option>
              {directions.map(dir => (
                <option key={dir} value={dir}>
                  {dir} {vastuRules.poojaRoom[dir] ? `(${vastuRules.poojaRoom[dir]})` : ''}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Error Display */}
        {Object.keys(errors).length > 0 && (
          <div style={formStyles.section}>
            <div style={formStyles.error}>
              {Object.values(errors).map((error, index) => (
                <div key={index}>{error}</div>
              ))}
            </div>
          </div>
        )}

        <button type="submit" style={formStyles.button}>
          Generate Floor Plans
        </button>
      </form>
    </div>
  );
};

export default VastuPlannerForm;