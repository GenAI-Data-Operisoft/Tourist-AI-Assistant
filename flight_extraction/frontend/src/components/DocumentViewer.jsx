import React, { useState } from 'react';
import { FileText, ChevronDown } from 'lucide-react';
import './DocumentViewer.css';

function DocumentViewer({ files, selectedDocument, onDocumentSelect }) {
  const [currentPage, setCurrentPage] = useState(0);

  if (!files || files.length === 0) {
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
    onDocumentSelect({ type: 'file', data: files[index] });
  };

  const currentFile = files[currentPage];
  const fileUrl = currentFile ? URL.createObjectURL(currentFile) : null;
  const isImage = currentFile && currentFile.type.startsWith('image/');
  const isPDF = currentFile && currentFile.type === 'application/pdf';

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
            {files.map((file, index) => (
              <option key={index} value={index}>
                {index + 1}. {file.name}
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
          {currentFile?.type || 'Unknown type'} • {(currentFile?.size / 1024).toFixed(1)} KB
        </span>
      </div>
    </div>
  );
}

export default DocumentViewer;
