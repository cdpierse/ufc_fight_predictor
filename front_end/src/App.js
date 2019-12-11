import React from 'react';
import logo from './logo.svg';
import './App.css';
import Navbar from './components/Navbar/Navbar'
import PredictionContainer from './components/FighterSelect/FighterSelect';

function App() {
  return (
    <div>
      <Navbar />
      <PredictionContainer />
    </div>
  );
}

export default App;
