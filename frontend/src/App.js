import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import VastuPlannerForm from './components/VastuPlannerForm';
import FloorPlanResults from './components/FloorPlanResults';
import AutoVastuForm from './components/AutoVastuForm';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Routes>
          <Route path="/results" element={<FloorPlanResults />} />
          <Route path="/" element={<AutoVastuForm />} />

        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;