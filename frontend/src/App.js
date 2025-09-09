// App.js
import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, useNavigate } from 'react-router-dom';
import './App.css';
import Dashboard from './Dashboard';
import { searchAPI } from './apiService';

// Genera queries para Google
const previewQueries = (tipo, texto) => {
  if (!texto) return [];
  let queries = [];

  if (tipo === "Nombre/Apellidos") {
    const partes = texto.trim().split(/\s+/);
    const nombre = partes[0] || "";
    const apellidos = partes.length > 1 ? partes.slice(1).join(" ") : "";
    queries = [
      `"${nombre} ${apellidos}"`,
      `"${apellidos} ${nombre}"`,
      `${nombre} ${apellidos}`,
      `"${nombre}" "${apellidos}"`
    ];
  } else if (tipo === "Nº Teléfono") {
    let tel = texto.replace(/\s|-/g, "");
    let telInt = tel.startsWith("+34") ? tel : (tel.length === 9 ? `+34${tel}` : tel);
    queries = [tel, telInt, `"${tel}"`, `"${telInt}"`];
  } else if (tipo === "Email") {
    queries = [texto, `"${texto}"`];
  } else if (tipo === "DNI") {
    let dni = texto.toUpperCase().replace(/\s/g, "");
    let base = dni.slice(0, -1);
    let letra = dni.slice(-1).match(/[A-Z]/) ? dni.slice(-1) : "";
    while (base.length < 8) base = "0" + base;

    queries = [base];
    if (letra) queries.push(base + letra);
    queries = [...queries, ...queries.map(q => `"${q}"`)];
  } else {
    queries = [texto, `"${texto}"`];
  }

  return queries;
};

function Home({ mode, setMode }) {
  const [photoCount, setPhotoCount] = useState('');
  const [rows, setRows] = useState([
    { text: '', dropdown1: '', dropdown2: '', selectedOption1: '', selectedOption2: '', optionsForDropdown2: ['Nombre/Apellidos','Nombre de usuario', 'Nº Teléfono', 'Email', 'DNI'] }
  ]);
  const navigate = useNavigate();

  const handleTextChange = (e, index) => {
    const newRows = [...rows];
    newRows[index].text = e.target.value;
    setRows(newRows);
  };

  const handleDropdown1Change = (e, index) => {
    const newRows = [...rows];
    newRows[index].dropdown1 = e.target.value;
    newRows[index].selectedOption1 = e.target.value !== '' ? e.target.options[e.target.selectedIndex].text : '';
    switch (e.target.value) {
      case 'Instagram':
        newRows[index].optionsForDropdown2 = ['Nombre de usuario'];
        break;
      case 'Google':
        newRows[index].optionsForDropdown2 = ['Nombre/Apellidos', 'Nº Teléfono', 'Email', 'DNI', 'Nombre de usuario'];
        break;
      case 'Twitter':
        newRows[index].optionsForDropdown2 = ['Nombre de usuario'];
        break;
      case 'LinkedIn':
        newRows[index].optionsForDropdown2 = ['URL del usuario'];
        break;               
      default:
        newRows[index].optionsForDropdown2 = ['Nombre de usuario', 'Nº Teléfono', 'Email', 'DNI'];
    }
    newRows[index].dropdown2 = '';
    newRows[index].selectedOption2 = '';
    setRows(newRows);
  };

  const handleDropdown2Change = (e, index) => {
    const newRows = [...rows];
    newRows[index].dropdown2 = e.target.value;
    newRows[index].selectedOption2 = e.target.options[e.target.selectedIndex].text;
    setRows(newRows);
  };

  const handleAddRow = () => {
    setRows([
      ...rows,
      { text: '', dropdown1: '', dropdown2: '', selectedOption1: '', selectedOption2: '', optionsForDropdown2: ['Nombre de usuario', 'Nº Teléfono', 'Email', 'DNI'] }
    ]);
  };

  const handleRemoveRow = (index) => {
    if (rows.length > 1) {
      const newRows = rows.filter((_, i) => i !== index);
      setRows(newRows);
    }
  };

  const handleSubmit = async () => {
    try {
      const enrichedRows = rows.map(row => ({
        ...row,
        numPhotos: photoCount || 3
      }));
      const response = await searchAPI({ rows: enrichedRows, mode });

      let normalized;
      if (response.results && Array.isArray(response.results)) {
        normalized = response.results;
      } else {
        normalized = [response];
      }

      navigate('/results', { state: { rows: enrichedRows, responseData: normalized } });
    } catch (error) {
      console.error('Error al enviar datos:', error);
    }
  };

  return (
    <div className="App">
      <div className="home-container">
        <div className="header">
          <h1 className="home-title"><span>Gestiona la Identidad Digital</span></h1>
          <select value={mode} onChange={(e) => setMode(e.target.value)} className="mode-select">
            <option value="development">Desarrollo</option>
            <option value="production">Producción</option>
          </select>
        </div>

        {rows.map((row, index) => (
          <div className="row" key={index}>
            <div className="input-block">
              <div className="selected-options">
                {row.selectedOption1 && <span className="selected-option1">{row.selectedOption1}</span>}
                {row.selectedOption1 && row.selectedOption2 && <span className="separator"> - </span>}
                {row.selectedOption2 && <span className="selected-option2">{row.selectedOption2}</span>}
              </div>
              <input
                type="text"
                value={row.text}
                onChange={(e) => handleTextChange(e, index)}
                placeholder="Escriba aquí"
              />
              <select onChange={(e) => handleDropdown1Change(e, index)} value={row.dropdown1}>
                <option value="">Seleccione plataforma</option>
                <option value="Google">Google</option>
                <option value="Instagram">Instagram</option>
                <option value="Twitter">Twitter</option>
                <option value="LinkedIn">LinkedIn</option>
              </select>
              <select onChange={(e) => handleDropdown2Change(e, index)} value={row.dropdown2}>
                <option value="">Seleccione</option>
                {row.optionsForDropdown2.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
              <div className="button-row">
                <button className="round-button remove" onClick={() => handleRemoveRow(index)}>-</button>
                {index === rows.length - 1 && (
                  <button className="round-button add" onClick={handleAddRow}>+</button>
                )}
              </div>
            </div>

            {row.selectedOption1 === "Google" && row.selectedOption2 && row.text && (
              <div style={{ marginTop: 6, fontSize: "0.85em", color: "#555" }}>
                <strong>Se buscarán:</strong>
                <div style={{ marginTop: 4, display: "flex", flexWrap: "wrap", gap: "6px" }}>
                  {previewQueries(row.selectedOption2, row.text).map((q, i) => (
                    <span 
                      key={i} 
                      style={{ 
                        background: "#cee4f1ff", 
                        padding: "4px 8px", 
                        borderRadius: "6px", 
                        fontSize: "0.82em", 
                        marginRight: "6px", 
                        whiteSpace: "pre-wrap", 
                        display: "inline-block" 
                      }}
                    >
                      {q}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
        <div className="row">
          <button className="search-button" onClick={handleSubmit}>Buscar</button>
        </div>
      </div>
    </div>
  );
}

function App() {
  const [mode, setMode] = useState("development");

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home mode={mode} setMode={setMode} />} />
        <Route path="/results" element={<Dashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
