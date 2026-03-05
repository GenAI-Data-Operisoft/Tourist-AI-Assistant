import React, { useState } from 'react';
import { FileText, ChevronDown } from 'lucide-react';
import './DocumentViewer.css';

function DocumentViewer({ files, fileMetadata, selectedDocument, onDocumentSelect }) {
  const [currentPage, setCurrentPage] = useState(0);

  // When using pre-signed URLs, all files are in S3 (fileMetadata)
  // Only show uploaded files if they haven't been uploaded to S3 yet
  const allFiles = [
    // Only show fileMetadata (all files are now in S3)
    ...(fileMetadata || []).map((meta, idx) => ({ 
      type: 's3', 
      bucket: meta.bucket,
      key: meta.key,
      name: meta.name,
      index: idx 
    }))
  ];

  if (allFiles.length === 0) {
    return (
      <div className="document-viewer">
        <div className="empty-state">
          <FileText size={48} color="#9ca3af" />
          <p>No documents to display</p>
        </div>
      </div>
    );
  }

  const handleDocumentChange = (e) => {
    const index = parseInt(e.target.value);
    setCurrentPage(index);
    const selectedFile = allFiles[index];
    onDocumentSelect(selectedFile);
  };

  const currentFile = allFiles[currentPage];
  
  // Generate URL for display
  let fileUrl = null;
  let isImage = false;
  let isPDF = false;

  if (currentFile) {
    if (currentFile.type === 'upload') {
      fileUrl = URL.createObjectURL(currentFile.file);
      isImage = currentFile.file.type.startsWith('image/');
      isPDF = currentFile.file.type === 'application/pdf';
    } else if (currentFile.type === 's3') {
      // Use the same host as API_BASE from App.jsx
      // Get the API base URL from window location or use the backend URL
      // const apiHost = window.location.hostname === 'localhost' 
      //   ? 'http://localhost:8001' 
      //   : `http://${window.location.hostname}:8001`;
      
      const apiHost = import.meta.env.VITE_API_BASE;

      fileUrl = `${apiHost}/s3-proxy/${currentFile.bucket}/${currentFile.key}`;
      // Detect type from key
      const keyLower = currentFile.key.toLowerCase();
      isPDF = keyLower.endsWith('.pdf');
      isImage = keyLower.match(/\.(jpg|jpeg|png)$/);
    }
  }

  return (
    <div className="document-viewer">
      <div className="viewer-header">
        <h3>📄 Document Preview</h3>
        <div className="document-selector">
          <select 
            value={currentPage} 
            onChange={handleDocumentChange}
            className="document-dropdown"
          >
            {allFiles.map((fileItem, index) => (
              <option key={index} value={index}>
                {index + 1}. {fileItem.name} {fileItem.type === 's3' ? '(S3)' : ''}
              </option>
            ))}
          </select>
          <ChevronDown size={16} className="dropdown-icon" />
        </div>
      </div>

      <div className="viewer-content">
        {fileUrl ? (
          <>
            {isPDF && (
              <iframe
                src={fileUrl}
                title={currentFile.name}
                className="pdf-iframe"
              />
            )}
            {isImage && (
              <div className="image-container">
                <img
                  src={fileUrl}
                  alt={currentFile.name}
                  className="document-image"
                />
              </div>
            )}
            {!isPDF && !isImage && (
              <div className="empty-state">
                <FileText size={48} color="#9ca3af" />
                <p>Unsupported file format</p>
                <a href={fileUrl} target="_blank" rel="noopener noreferrer" className="s3-fallback-link">
                  Open in New Tab
                </a>
              </div>
            )}
          </>
        ) : (
          <div className="empty-state">
            <FileText size={48} color="#9ca3af" />
            <p>Unable to load document</p>
          </div>
        )}
      </div>

      <div className="viewer-footer">
        <span className="file-name">{currentFile?.name}</span>
        <span className="file-type">
          {currentFile?.type === 's3' ? 'S3 File' : (currentFile?.file?.type || 'Unknown type')}
          {currentFile?.type === 'upload' && currentFile?.file?.size && 
            ` • ${(currentFile.file.size / 1024).toFixed(1)} KB`}
        </span>
      </div>
    </div>
  );
}

export default DocumentViewer;
