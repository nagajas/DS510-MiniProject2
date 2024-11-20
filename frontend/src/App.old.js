import React, { useState } from 'react';
import axios from 'axios';
//import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [language, setLanguage] = useState('Hindi');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const languages = ['English', 'Hindi', 'Tamil', 'Telugu', 'Marathi', 'Kannada'];

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleLanguageChange = (e) => {
    setLanguage(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('language', language);

    setLoading(true);
    setResult(null);

    try {
      const response = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResult(response.data);
    } catch (error) {
      console.error(error);
      alert('Error uploading file');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Image Caption Translator</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Select Image:</label>
          <input type="file" accept=".png,.jpg,.jpeg" onChange={handleFileChange} required />
        </div>
        <div className="form-group">
          <label>Select Language:</label>
          <select value={language} onChange={handleLanguageChange}>
            {languages.map((lang) => (
              <option key={lang} value={lang}>{lang}</option>
            ))}
          </select>
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Upload and Process'}
        </button>
      </form>

      {result && (
        <div className="results">
          <h2>Results</h2>
          <img 
            src={`/uploads/${result.filename}`} 
            alt="Uploaded" 
          />
          <p><strong>English Caption:</strong> {result.caption}</p>
          <p><strong>Translated Caption ({language}):</strong> {result.translated}</p>
          <audio controls>
            <source src={`/uploads/${result.audio_file}`} type="audio/mpeg" />
            Your browser does not support the audio element.
          </audio>
        </div>
      )}
    </div>
  );
}

export default App;