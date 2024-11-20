import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [language, setLanguage] = useState('Hindi');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Base URL for the API
  const BASE_URL = 'http://10.10.209.200:5000';

  const languages = ['English', 'Hindi', 'Tamil', 'Telugu', 'Marathi', 'Kannada'];

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleLanguageChange = (e) => {
    setLanguage(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      alert('Please select a file before submitting.');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('language', language);

    setLoading(true);
    setResult(null);

    try {
      const response = await axios.post(`${BASE_URL}/api/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResult(response.data);
    } catch (error) {
      console.error(error);
      alert('Error uploading file or processing the request.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-100 to-indigo-200 flex items-center justify-center p-4">
      <div className="w-full max-w-xl bg-white shadow-lg rounded-lg p-8">
        <h1 className="text-3xl font-semibold text-center text-gray-800 mb-6">Image Caption Translator</h1>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-gray-700 font-medium mb-2">Select Image:</label>
            <input
              type="file"
              accept=".png,.jpg,.jpeg"
              onChange={handleFileChange}
              required
              className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>
          <div>
            <label className="block text-gray-700 font-medium mb-2">Select Language:</label>
            <select
              value={language}
              onChange={handleLanguageChange}
              className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400"
            >
              {languages.map((lang) => (
                <option key={lang} value={lang}>
                  {lang}
                </option>
              ))}
            </select>
          </div>
          <button
            type="submit"
            disabled={loading}
            className={`w-full py-2 px-4 bg-indigo-600 text-white font-semibold rounded-md hover:bg-indigo-700 transition-colors ${
              loading ? 'cursor-not-allowed bg-indigo-400' : ''
            }`}
          >
            {loading ? 'Processing...' : 'Upload and Process'}
          </button>
        </form>

        {result && (
          <div className="mt-8 p-6 bg-gray-50 rounded-lg shadow-inner">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">Results</h2>
            <div className="mb-4">
              <img
                src={`${BASE_URL}/static/uploads/${result.filename}`}
                alt="Uploaded file"
                className="w-full h-auto rounded-md shadow-md"
              />
            </div>
            <div className="mb-4">
              <p className="text-lg text-gray-700">
                <span className="font-semibold">English Caption:</span> {result.caption}
              </p>
            </div>
            <div className="mb-4">
              <p className="text-lg text-gray-700">
                <span className="font-semibold">Translated Caption ({language}):</span> {result.translated}
              </p>
            </div>
            <div className="mb-4">
              <audio controls className="w-full" aria-label="Audio narration of translated caption">
                <source
                  src={`${BASE_URL}/static/uploads/${result.audio_file}`}
                  type="audio/mp3"
                />
                Your browser does not support the audio element.
              </audio>
            </div>
            <button
              onClick={() => setResult(null)}
              className="mt-4 w-full py-2 px-4 bg-red-500 text-white font-semibold rounded-md hover:bg-red-600 transition-colors"
            >
              Upload Another Image
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
