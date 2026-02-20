import React, { useState } from 'react';
import axios from 'axios';
import { Upload, Link as LinkIcon, FileText, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import DocumentViewer from './components/DocumentViewer';
import ResultsPanel from './components/ResultsPanel';
import './App.css';

const API_BASE = 'http://localhost:8001';
// const API_BASE = 'http://13.201.173.21:8001';


function App() {
  const [files, setFiles] = useState([]);
  const [s3Links, setS3Links] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [processingStatus, setProcessingStatus] = useState(null);
  const [fileErrors, setFileErrors] = useState([]);
  const [fileMetadata, setFileMetadata] = useState([]);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(selectedFiles);
    if (selectedFiles.length > 0) {
      setSelectedDocument({ type: 'file', data: selectedFiles[0] });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);
    setFileErrors([]);
    setProcessingStatus(null);

    try {
      const formData = new FormData();
      
      // Add files
      files.forEach(file => {
        formData.append('files', file);
      });

      // Parse S3 links
      const s3UrlArray = s3Links
        .split('\n')
        .map(link => link.trim())
        .filter(link => link.length > 0);

      // Show processing status
      const totalFiles = files.length + s3UrlArray.length;
      setProcessingStatus({
        total: totalFiles,
        current: 0,
        message: 'Starting processing...'
      });

      let response;
      
      if (files.length > 0 && s3UrlArray.length > 0) {
        // Mixed: both files and S3
        setProcessingStatus({
          total: totalFiles,
          current: 0,
          message: `Processing ${files.length} uploaded file(s) and ${s3UrlArray.length} S3 link(s)...`
        });
        
        formData.append('s3_urls', JSON.stringify(s3UrlArray));
        response = await axios.post(`${API_BASE}/extract/mixed`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
          params: { s3_urls: s3UrlArray }
        });
      } else if (files.length > 0) {
        // Only files
        setProcessingStatus({
          total: totalFiles,
          current: 0,
          message: `Processing ${files.length} uploaded file(s)...`
        });
        
        response = await axios.post(`${API_BASE}/extract/upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      } else if (s3UrlArray.length > 0) {
        // Only S3
        setProcessingStatus({
          total: s3UrlArray.length,
          current: 0,
          message: `Processing ${s3UrlArray.length} S3 link(s) one by one...`
        });
        
        response = await axios.post(`${API_BASE}/extract/s3`, {
          s3_urls: s3UrlArray
        });
      } else {
        throw new Error('Please upload files or provide S3 links');
      }

      setResults(response.data.results);
      
      // Store file metadata for document viewer
      if (response.data.files) {
        setFileMetadata(response.data.files);
      }
      
      // Handle errors from individual files
      if (response.data.errors && response.data.errors.length > 0) {
        setFileErrors(response.data.errors);
      }
      
      // Show summary
      if (response.data.summary) {
        const { successful, failed, total } = response.data.summary;
        if (failed > 0) {
          setError(`Processed ${successful}/${total} files successfully. ${failed} file(s) failed.`);
        }
      }
      
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred');
    } finally {
      setLoading(false);
      setProcessingStatus(null);
    }
  };

  const handleReset = () => {
    setFiles([]);
    setS3Links('');
    setResults(null);
    setError(null);
    setSelectedDocument(null);
    setFileErrors([]);
    setProcessingStatus(null);
    setFileMetadata([]);
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1>🧳 Travel Document Extractor</h1>
          <p>AI-powered extraction for flights, trains, and hotels</p>
        </div>
      </header>

      <main className="main-content">
        {!results ? (
          <div className="upload-section">
            <form onSubmit={handleSubmit} className="upload-form">
              <div className="input-group">
                <label className="input-label">
                  <Upload size={20} />
                  <span>Upload PDF or Image Files</span>
                </label>
                <input
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  multiple
                  onChange={handleFileChange}
                  className="file-input"
                  id="file-upload"
                />
                <label htmlFor="file-upload" className="file-input-label">
                  {files.length > 0 ? `${files.length} file(s) selected` : 'Choose files (PDF, JPG, PNG)...'}
                </label>
              </div>

              <div className="divider">
                <span>OR</span>
              </div>

              <div className="input-group">
                <label className="input-label">
                  <LinkIcon size={20} />
                  <span>S3 Links (one per line)</span>
                </label>
                <textarea
                  value={s3Links}
                  onChange={(e) => setS3Links(e.target.value)}
                  placeholder="s3://bucket/path/file.pdf&#10;https://bucket.s3.region.amazonaws.com/image.jpg"
                  className="textarea-input"
                  rows={4}
                />
              </div>

              {error && (
                <div className="error-message">
                  <AlertCircle size={20} />
                  <span>{error}</span>
                </div>
              )}

              {processingStatus && (
                <div className="processing-status">
                  <Loader2 size={20} className="spinner" />
                  <div className="status-text">
                    <div>{processingStatus.message}</div>
                    <div className="status-detail">
                      Processing {processingStatus.total} file(s)...
                    </div>
                  </div>
                </div>
              )}

              {fileErrors.length > 0 && !loading && (
                <div className="file-errors">
                  <div className="errors-header">
                    <AlertCircle size={18} />
                    <span>Some files failed to process:</span>
                  </div>
                  <ul className="errors-list">
                    {fileErrors.map((err, idx) => (
                      <li key={idx}>
                        <strong>{err.name || err.url}:</strong> {err.error}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <button
                type="submit"
                disabled={loading || (files.length === 0 && !s3Links.trim())}
                className="submit-button"
              >
                {loading ? (
                  <>
                    <Loader2 size={20} className="spinner" />
                    Processing...
                  </>
                ) : (
                  <>
                    <FileText size={20} />
                    Extract Data
                  </>
                )}
              </button>
            </form>
          </div>
        ) : (
          <div className="results-section">
            <div className="results-header">
              <div className="results-info">
                <CheckCircle size={24} color="#10b981" />
                <h2>{results.length} Booking(s) Extracted</h2>
              </div>
              <button onClick={handleReset} className="reset-button">
                Process New Documents
              </button>
            </div>

            <div className="split-view">
              <DocumentViewer
                files={files}
                fileMetadata={fileMetadata}
                selectedDocument={selectedDocument}
                onDocumentSelect={setSelectedDocument}
              />
              <ResultsPanel results={results} />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
