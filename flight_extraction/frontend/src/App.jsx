import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, Link as LinkIcon, FileText, Loader2, CheckCircle, AlertCircle, LogOut } from 'lucide-react';
import DocumentViewer from './components/DocumentViewer';
import ResultsPanel from './components/ResultsPanel';
import Login from './Login';
import './App.css';

// Determine API base URL based on environment
// const API_BASE = window.location.hostname === 'localhost' 
//   ? 'http://localhost:8001' 
//   : 'http://65.2.55.2:8001';

const API_BASE = import.meta.env.VITE_API_BASE;

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [files, setFiles] = useState([]);
  const [s3Links, setS3Links] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [fileMetadata, setFileMetadata] = useState([]);
  const [error, setError] = useState(null);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [processingStatus, setProcessingStatus] = useState(null);
  const [fileErrors, setFileErrors] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const storedUsername = localStorage.getItem('username');
    if (token) {
      setIsAuthenticated(true);
      setUsername(storedUsername || 'User');
    }
  }, []);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    
    // Validate file types
    const supportedExtensions = ['.pdf', '.jpg', '.jpeg', '.png'];
    const unsupportedFiles = [];
    const validFiles = [];
    
    selectedFiles.forEach(file => {
      const fileName = file.name.toLowerCase();
      const isSupported = supportedExtensions.some(ext => fileName.endsWith(ext));
      
      if (isSupported) {
        validFiles.push(file);
      } else {
        unsupportedFiles.push(file.name);
      }
    });
    
    // Show error popup for unsupported files
    if (unsupportedFiles.length > 0) {
      const fileList = unsupportedFiles.join('\n• ');
      alert(
        `❌ Unsupported File Format\n\n` +
        `The following file(s) are not supported:\n\n• ${fileList}\n\n` +
        `Supported formats: PDF, JPG, JPEG, PNG`
      );
    }
    
    // Only set valid files
    if (validFiles.length > 0) {
      setFiles(validFiles);
      setSelectedDocument({ type: 'file', data: validFiles[0] });
    } else if (unsupportedFiles.length > 0) {
      // Clear file input if all files are invalid
      e.target.value = '';
      setFiles([]);
    }
  };

  // Helper function to upload file using pre-signed URL
  const uploadFileToS3 = async (file) => {
    // Step 1: Get pre-signed URL
    const urlResponse = await axios.post(`${API_BASE}/generate-upload-url`, {
      filename: file.name,
      content_type: file.type
    });

    const { upload_url, fields, s3_url, bucket, key, original_filename } = urlResponse.data;

    // Step 2: Upload to S3 using pre-signed URL
    const formData = new FormData();
    
    // Add all fields from pre-signed POST
    Object.keys(fields).forEach(key => {
      formData.append(key, fields[key]);
    });
    
    // Add the file (must be last)
    formData.append('file', file);

    // Upload to S3 (direct, bypasses API Gateway)
    await axios.post(upload_url, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    // Return S3 URL with metadata including original filename
    return {
      s3_url,
      bucket,
      key,
      name: original_filename,
      source: 's3'
    };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);
    setFileErrors([]);
    setProcessingStatus(null);

    try {
      // Parse S3 links from textarea (these are EXISTING S3 files, don't re-upload)
      const existingS3Urls = s3Links
        .split('\n')
        .map(link => link.trim())
        .filter(link => link.length > 0);

      const totalFiles = files.length + existingS3Urls.length;
      
      if (totalFiles === 0) {
        throw new Error('Please upload files or provide S3 links');
      }
      
      // Upload NEW files to S3 using pre-signed URLs
      const uploadedS3Urls = [];
      const uploadedMetadata = [];
      
      if (files.length > 0) {
        setProcessingStatus({
          total: totalFiles,
          current: 0,
          message: `Uploading ${files.length} file(s) to S3...`
        });

        for (let i = 0; i < files.length; i++) {
          const file = files[i];
          
          setProcessingStatus({
            total: totalFiles,
            current: i,
            message: `Uploading ${file.name} (${i + 1}/${files.length})...`
          });

          try {
            const uploadResult = await uploadFileToS3(file);
            uploadedS3Urls.push(uploadResult.s3_url);
            uploadedMetadata.push(uploadResult);  // Store metadata with original filename
          } catch (err) {
            setFileErrors(prev => [...prev, {
              name: file.name,
              error: `Upload failed: ${err.message}`
            }]);
          }
        }
      }

      // Combine: newly uploaded files + existing S3 links (no duplicates)
      const allS3Urls = [...uploadedS3Urls, ...existingS3Urls];

      if (allS3Urls.length === 0) {
        throw new Error('No files to process');
      }

      // Process all files from S3
      setProcessingStatus({
        total: allS3Urls.length,
        current: 0,
        message: `Processing ${allS3Urls.length} file(s)...`
      });

      const response = await axios.post(`${API_BASE}/extract/s3`, {
        s3_urls: allS3Urls
      });

      setResults(response.data.results);
      
      // Use uploaded metadata for files we uploaded, and response metadata for existing S3 files
      // Match by S3 URL to avoid duplicates
      const responseMetadata = response.data.files || [];
      const uploadedS3UrlSet = new Set(uploadedS3Urls);
      
      // Filter out response metadata for files we just uploaded (to avoid duplicates)
      const existingS3Metadata = responseMetadata.filter(meta => {
        const metaUrl = meta.url || `s3://${meta.bucket}/${meta.key}`;
        return !uploadedS3UrlSet.has(metaUrl);
      });
      
      // Combine: uploaded files (with original names) + existing S3 files
      const combinedMetadata = [
        ...uploadedMetadata,      // Files we just uploaded (original names)
        ...existingS3Metadata     // Existing S3 files from textarea
      ];
      
      setFileMetadata(combinedMetadata);
      
      // Handle errors from processing
      if (response.data.errors && response.data.errors.length > 0) {
        setFileErrors(prev => [...prev, ...response.data.errors]);
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
    setFileMetadata([]);
    setError(null);
    setSelectedDocument(null);
    setFileErrors([]);
    setProcessingStatus(null);
  };

  return (
    <div className="app">
      {!isAuthenticated ? (
        <Login onSuccess={(user) => {
          setIsAuthenticated(true);
          setUsername(user);
        }} />
      ) : (
        <>
          <header className="header">
            <div className="header-content">
              <h1>🧳 Tourish AI ASSISTANT</h1>
              <p>AI-powered extraction for flights, trains, and hotels</p>
            </div>
            <div className="user-info">
              <div className="username">{username}</div>
              <button
                onClick={() => {
                  localStorage.removeItem('token');
                  localStorage.removeItem('username');
                  setIsAuthenticated(false);
                  setUsername('');
                  handleReset();
                }}
                className="logout-button"
              >
                <LogOut size={18} />
                Logout
              </button>
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
        </>
      )}
    </div>
  );
}

export default App;
