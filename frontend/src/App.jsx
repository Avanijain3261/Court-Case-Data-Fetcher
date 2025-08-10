import React, { useState } from 'react';
import axios from 'axios';
import './App.css'; // Import our custom CSS

// A simple component for displaying loading spinners
const Spinner = () => (
  <div className="spinner-container">
    <div className="spinner"></div>
  </div>
);

function App() {
  // State to hold the form input values
  const [caseDetails, setCaseDetails] = useState({
    case_type: 'W.P.(C)',
    case_number: '5595',
    case_year: '2021',
  });

  // State to hold the data returned from the API
  const [result, setResult] = useState(null);
  // State to hold any errors
  const [error, setError] = useState('');
  // State to manage the loading indicator
  const [isLoading, setIsLoading] = useState(false);

  // Function to handle changes in the input fields
  const handleChange = (e) => {
    const { name, value } = e.target;
    setCaseDetails((prevDetails) => ({
      ...prevDetails,
      [name]: value,
    }));
  };

  // Function to handle the form submission
  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent the default form submission behavior
    setIsLoading(true);
    setError('');
    setResult(null);

    try {
      const API_URL = 'http://127.0.0.1:8000/api/fetch-case';
      const response = await axios.post(API_URL, {
        case_type: caseDetails.case_type,
        case_number: caseDetails.case_number,
        case_year: caseDetails.case_year,
      });
      setResult(response.data);
    } catch (err) {
      if (err.response) {
        setError(`Error: ${err.response.data.detail || 'Failed to fetch case details.'}`);
      } else {
        setError('An unexpected error occurred. Is the backend server running?');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-content">
          <h1>Court Case Data Fetcher</h1>
          <p>Delhi High Court</p>
        </div>
      </header>

      <main className="app-main">
        <div className="form-card">
          <form onSubmit={handleSubmit}>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="case_type">Case Type</label>
                <input
                  type="text"
                  name="case_type"
                  id="case_type"
                  value={caseDetails.case_type}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="case_number">Case Number</label>
                <input
                  type="text"
                  name="case_number"
                  id="case_number"
                  value={caseDetails.case_number}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="case_year">Case Year</label>
                <input
                  type="text"
                  name="case_year"
                  id="case_year"
                  value={caseDetails.case_year}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>
            <div className="form-actions">
              <button type="submit" disabled={isLoading}>
                {isLoading ? 'Searching...' : 'Search Case'}
              </button>
            </div>
          </form>
        </div>

        <div className="results-container">
          {isLoading && <Spinner />}
          {error && (
            <div className="error-box">
              <p><strong>Error</strong></p>
              <p>{error}</p>
            </div>
          )}
          {result && (
            <div className="result-card">
              <h2 className="section-title">Case Details</h2>
              <div className="result-grid">
                <div>
                  <h3>Parties</h3>
                  <p>{result.party_names}</p>
                </div>
                <div>
                  <h3>Filing Info</h3>
                  <p>{result.filing_date}</p>
                </div>
                <div>
                  <h3>Next Hearing Date</h3>
                  <p>{result.next_hearing_date}</p>
                </div>
                
                <div>
                  <h3>Main Orders Page</h3>
                   <a href={result.orders_link} target="_blank" rel="noopener noreferrer">
                    View All Orders
                  </a>
                </div>
              </div>
              
              <div className="orders-section">
                <h2 className="section-title">Downloadable Orders</h2>
                {result.orders && result.orders.length > 0 ? (
                  <div className="orders-table">
                    <div className="orders-header">
                      <div>Date of Order</div>
                      <div>Download</div>
                    </div>
                    {result.orders.map((order, index) => (
                      <div className="order-row" key={index}>
                        <div>{order.date}</div>
                        <div>
                          <a 
                            href={order.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="download-button"
                            download
                          >
                            Download PDF
                          </a>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p>No downloadable orders found for this case.</p>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
