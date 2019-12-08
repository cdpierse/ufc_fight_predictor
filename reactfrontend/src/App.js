import React from 'react';
import logo from './logo.svg';
import './App.css';
import Navbar from './components/Navbar/Navbar'
import SelectionGrid from './containers/FighterSelect/FighterSelect'

function App() {
  return (
    <div>
      <Navbar />
      <SelectionGrid />
    </div>
  );
}

export default App;
