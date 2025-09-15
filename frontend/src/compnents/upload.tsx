import React, { useState, useRef, useEffect } from "react";
import "./upload.css";
import { ArrowLeft, Upload as UploadIcon, FileText, X, Check, Sparkles, Cloud, User, ChevronDown, History, Star } from "lucide-react";
import { useNavigate } from "react-router-dom";

interface UserData {
  q_a: Array<{question: string, answer: string}>;
  user_name: string;
  points: string[];
}

const Upload: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadedFileName, setUploadedFileName] = useState<string>("");
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [isDragOver, setIsDragOver] = useState<boolean>(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [showSuccess, setShowSuccess] = useState<boolean>(false);
  const [userData, setUserData] = useState<UserData | null>(null);
  const [showUserDropdown, setShowUserDropdown] = useState<boolean>(false);
  const [isLoadingUser, setIsLoadingUser] = useState<boolean>(true);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  // Particle animation effect
  const [particles, setParticles] = useState<Array<{id: number, x: number, y: number, delay: number}>>([]);

  useEffect(() => {
    // Generate particles for background animation
    const newParticles = Array.from({length: 20}, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      delay: Math.random() * 3
    }));
    setParticles(newParticles);

    // Fetch user history
    fetchUserHistory();
  }, []);

  const fetchUserHistory = async () => {
    try {
      setIsLoadingUser(true);
      const response = await fetch("http://localhost:8001/user_history");
      if (response.ok) {
        const data = await response.json();
        setUserData(data);
      } else {
        console.error("Failed to fetch user history");
      }
    } catch (error) {
      console.error("Error fetching user history:", error);
    } finally {
      setIsLoadingUser(false);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
      setShowSuccess(false);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = e.dataTransfer.files;
    if (files && files[0]) {
      setSelectedFile(files[0]);
      setShowSuccess(false);
    }
  };

  const simulateProgress = () => {
    setUploadProgress(0);
    const interval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + Math.random() * 15 + 5;
      });
    }, 200);
    return interval;
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    setShowSuccess(false);

    const progressInterval = simulateProgress();

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch("http://localhost:9001/upload_file", {
        method: "POST",
        body: formData,
      });

      await new Promise(resolve => setTimeout(resolve, 1000)); // Ensure progress completes

      if (response.ok) {
        const data = await response.json();
        setUploadedFileName(data.filename);
        setShowSuccess(true);
        // Refresh user history to get updated file list
        fetchUserHistory();
        setTimeout(() => setShowSuccess(false), 3000);
      } else {
        setUploadedFileName("Upload failed!");
      }
    } catch (error) {
      console.error("Upload error:", error);
      setUploadedFileName("Error uploading file.");
    } finally {
      clearInterval(progressInterval);
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const removeFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    setUploadedFileName("");
    setSelectedFile(null);
    setShowSuccess(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'pdf':
        return <FileText size={20} className="file-icon-pdf" />;
      case 'txt':
        return <FileText size={20} className="file-icon-txt" />;
      case 'docx':
        return <FileText size={20} className="file-icon-docx" />;
      case 'csv':
        return <FileText size={20} className="file-icon-csv" />;
      default:
        return <FileText size={20} />;
    }
  };

  return (
    <div className="upload-container">
      {/* Enhanced Animated Background */}
      <div className="background-animation">
        {particles.map(particle => (
          <div
            key={particle.id}
            className="particle"
            style={{
              left: `${particle.x}%`,
              top: `${particle.y}%`,
              animationDelay: `${particle.delay}s`
            }}
          />
        ))}
        <div className="gradient-orbs">
          <div className="orb orb-1"></div>
          <div className="orb orb-2"></div>
          <div className="orb orb-3"></div>
        </div>
      </div>

      {/* Enhanced Header with User Info */}
      <header className="upload-header">
        <div className="header-content">
          <button className="back-button" onClick={() => navigate("/chat")}>
            <ArrowLeft size={18} /> 
            <span>Back to Chat</span>
          </button>
          
          <div className="header-info">
            <div className="bot-avatar">
              <Cloud size={28} />
              <div className="avatar-glow"></div>
            </div>
            <div className="header-text">
              <h2>
                <Sparkles size={20} className="sparkle-icon" />
                Smart File Upload
              </h2>
              <span className="status">Drag, drop, and let the magic happen</span>
            </div>
          </div>

          {/* User Profile Section */}
          <div className="user-profile">
            {isLoadingUser ? (
              <div className="user-loading">
                <div className="loading-spinner-small"></div>
              </div>
            ) : userData ? (
              <div className="user-info">
                <button 
                  className="user-button"
                  onClick={() => setShowUserDropdown(!showUserDropdown)}
                >
                  <div className="user-avatar">
                    <User size={20} />
                  </div>
                  <div className="user-details">
                    <span className="user-name">{userData.user_name}</span>
                    <span className="user-files">{userData.points.length} files</span>
                  </div>
                  <ChevronDown size={16} className={`dropdown-icon ${showUserDropdown ? 'rotated' : ''}`} />
                </button>

                {showUserDropdown && (
                  <div className="user-dropdown">
                    <div className="dropdown-header">
                      <History size={16} />
                      <span>Your Files</span>
                    </div>
                    <div className="user-files-list">
                      {userData.points.length > 0 ? (
                        userData.points.map((fileName, index) => (
                          <div key={index} className="dropdown-file-item">
                            {getFileIcon(fileName)}
                            <span className="file-name">{fileName}</span>
                            <Star size={12} className="file-star" />
                          </div>
                        ))
                      ) : (
                        <div className="no-files-dropdown">
                          <FileText size={16} />
                          <span>No files uploaded yet</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ) : null}
          </div>
        </div>
      </header>

      {/* Main Content - Side by Side Layout */}
      <div className="upload-content">
        {/* Upload Section - Left Side */}
        <section className="upload-section">
          <div className="section-header">
            <h3>Upload Your File Take Some Time</h3>
            <p>Transform your documents into searchable knowledge</p>
          </div>

          <label
            className={`upload-zone ${isDragOver ? 'drag-over' : ''} ${isUploading ? 'uploading' : ''} ${selectedFile ? 'has-file' : ''}`}
            htmlFor="fileInput"
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <div className="upload-zone-content">
              {!selectedFile ? (
                <>
                  <div className="upload-icon-container">
                    <UploadIcon size={48} className="upload-icon" />
                    <div className="icon-pulse"></div>
                  </div>
                  <h3>Drop your file here</h3>
                  <p>or click to browse your device</p>
                  <div className="supported-formats">
                    <span className="format-tag">PDF</span>
                    <span className="format-tag">TXT</span>
                    <span className="format-tag">DOCX</span>
                    <span className="format-tag">CSV</span>
                  </div>
                </>
              ) : (
                <div className="selected-file-preview">
                  <div className="file-preview-icon">
                    {getFileIcon(selectedFile.name)}
                  </div>
                  <div className="file-preview-info">
                    <h4>{selectedFile.name}</h4>
                    <p>{formatFileSize(selectedFile.size)}</p>
                  </div>
                  <button
                    type="button"
                    className="remove-preview-file"
                    onClick={removeFile}
                  >
                    <X size={16} />
                  </button>
                </div>
              )}
            </div>
            
            <input
              ref={fileInputRef}
              id="fileInput"
              type="file"
              className="file-input-hidden"
              accept=".pdf,.txt,.docx,.csv"
              onChange={handleFileChange}
            />
          </label>

          {/* Upload Progress */}
          {isUploading && (
            <div className="upload-progress-container">
              <div className="upload-progress">
                <div 
                  className="progress-bar" 
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
              <span className="progress-text">{Math.round(uploadProgress)}% uploaded</span>
            </div>
          )}

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={!selectedFile || isUploading}
            className={`upload-button ${isUploading ? 'uploading' : ''} ${showSuccess ? 'success' : ''}`}
          >
            {isUploading ? (
              <>
                <div className="loading-spinner"></div>
                <span>Processing...</span>
              </>
            ) : showSuccess ? (
              <>
                <Check size={20} />
                <span>Upload Complete!</span>
              </>
            ) : (
              <>
                <UploadIcon size={20} />
                <span>Upload File</span>
              </>
            )}
          </button>
        </section>

        {/* Files Section - Right Side */}
        <section className="files-section">
          <div className="files-header">
            <h3>
              <FileText size={24} />
              Your Files
            </h3>
            <div className="files-count">
              {userData ? `${userData.points.length} files` : "0 files"}
            </div>
          </div>

          <div className="files-list">
            {!userData || userData.points.length === 0 ? (
              <div className="no-files">
                <div className="no-files-illustration">
                  <Cloud size={64} className="cloud-icon" />
                  <div className="floating-docs">
                    <FileText size={24} className="doc-1" />
                    <FileText size={20} className="doc-2" />
                    <FileText size={18} className="doc-3" />
                  </div>
                </div>
                <h4>Your uploaded files will appear here</h4>
                <p>Upload your first document to get started with AI-powered search and analysis</p>
              </div>
            ) : (
              <div className="files-grid">
                {userData.points.map((fileName, index) => (
                  <div key={index} className={`file-item ${uploadedFileName === fileName ? 'success-animation' : 'success'}`}>
                    <div className="file-info">
                      <div className="file-icon">
                        {getFileIcon(fileName)}
                        <div className="file-icon-glow"></div>
                      </div>
                      <div className="file-details">
                        <h4>{fileName}</h4>
                        <div className="file-meta">
                          <span className="status-badge success">
                            <Check size={12} />
                            Ready for AI Analysis
                          </span>
                          <span className="upload-time">
                            {uploadedFileName === fileName ? 'Just now' : 'Previously uploaded'}
                          </span>
                        </div>
                      </div>
                    </div>
                    <button
                      className="remove-file"
                      onClick={() => {
                        // Handle file removal here if needed
                        console.log('Remove file:', fileName);
                      }}
                      title="Remove file"
                    >
                      <X size={16} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
};

export default Upload;