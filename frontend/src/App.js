import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import VastuPlannerForm from './components/VastuPlannerForm';
import FloorPlanResults from './components/FloorPlanResults';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Routes>
          <Route path="/" element={<VastuPlannerForm />} />
          <Route path="/results" element={<FloorPlanResults />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;