import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Demo.css';

const Demo = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('normal');
  const [customStartupName, setCustomStartupName] = useState('');
  const [customFile, setCustomFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadComplete, setUploadComplete] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingTimer, setProcessingTimer] = useState(0);
  const [uploadId, setUploadId] = useState(null);
  const [error, setError] = useState(null);
  const [countdown, setCountdown] = useState(300); // 5 minutes = 300 seconds
  const [isCountingDown, setIsCountingDown] = useState(false);
  const [pollingStarted, setPollingStarted] = useState(false);
  const fileInputRef = useRef(null);
  const pollTimeoutRef = useRef(null);

  const normalStartupName = "Inlustro_Demo";
  const normalZipFile = { name: "Inlustro.zip", size: "8.2 MB", url: process.env.PUBLIC_URL + "/Inlustro.zip" };

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

  useEffect(() => {
    let interval;
    if (isProcessing && processingTimer < 300) {
      interval = setInterval(() => {
        setProcessingTimer(prev => prev + 1);
      }, 1000);
    } else if (processingTimer >= 300) {
      setIsProcessing(false);
      navigate('/results', { state: { uploadId } });
    }
    return () => clearInterval(interval);
  }, [isProcessing, processingTimer, navigate, uploadId]);

  useEffect(() => {
    let interval;
    if (isCountingDown && countdown > 0) {
      interval = setInterval(() => {
        setCountdown(prev => prev - 1);
      }, 1000);
    } else if (countdown === 0 && isCountingDown) {
      setIsCountingDown(false);
      // Just update UI state, polling already started
    }
    return () => clearInterval(interval);
  }, [isCountingDown, countdown]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (pollTimeoutRef.current) {
        clearInterval(pollTimeoutRef.current.imagePolling);
        clearInterval(pollTimeoutRef.current.pdfPolling);
      }
    };
  }, []);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.type !== 'application/zip' && !file.name.endsWith('.zip')) {
        alert('Please select a ZIP file only');
        return;
      }
      setCustomFile(file);
    }
  };

  const handleUpload = async () => {
    if (activeTab === 'custom' && (!customStartupName.trim() || !customFile)) {
      alert('Please provide startup name and select a ZIP file');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);
    setError(null);

    try {
      const formData = new FormData();
      
      if (activeTab === 'normal') {
        // For normal demo, fetch the actual file from public directory
        const response = await fetch(normalZipFile.url);
        const blob = await response.blob();
        const actualFile = new File([blob], normalZipFile.name, { type: 'application/zip' });
        formData.append('startup_name', normalStartupName);
        formData.append('file', actualFile);
      } else {
        formData.append('startup_name', customStartupName);
        formData.append('file', customFile);
      }

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + Math.random() * 20;
        });
      }, 200);

      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      clearInterval(progressInterval);
      setUploadProgress(100);
      
      if (response.data && response.data.upload_id) {
        setUploadId(response.data.upload_id);
        setIsUploading(false);
        setUploadComplete(true);
        
        // Start 5-minute countdown timer and immediate polling
        setCountdown(300); // Reset to 5 minutes
        setIsCountingDown(true);
        
        // Start polling immediately in background
        if (!pollingStarted) {
          setPollingStarted(true);
          startPolling(response.data.upload_id);
        }
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      console.error('Upload failed:', error);
      setError(error.response?.data?.message || error.message || 'Upload failed');
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const startPolling = async (id) => {
    let imagePolls = 0;
    let pdfPolls = 0;
    const maxPolls = 180;
    
    // Start polling both APIs immediately
    const imagePolling = setInterval(async () => {
      imagePolls++;
      try {
        const response = await axios.get(`${API_BASE_URL}/status/images?upload_id=${id}`);
        // Stop polling when ANY response is received (completed, failed, processing, etc.)
        if (response.data && response.data.status) {
          clearInterval(imagePolling);
          clearInterval(pdfPolling);
          if (pollTimeoutRef.current) {
            pollTimeoutRef.current = null;
          }
          navigate('/results', { state: { uploadId: id } });
          return;
        }
      } catch (error) {
        console.error('Error polling images:', error);
      }
      
      if (imagePolls >= maxPolls) {
        clearInterval(imagePolling);
      }
    }, 10000);

    const pdfPolling = setInterval(async () => {
      pdfPolls++;
      try {
        const response = await axios.get(`${API_BASE_URL}/status/pdf?upload_id=${id}`);
        // Stop polling when ANY response is received (completed, failed, processing, etc.)
        if (response.data && response.data.status) {
          clearInterval(imagePolling);
          clearInterval(pdfPolling);
          if (pollTimeoutRef.current) {
            pollTimeoutRef.current = null;
          }
          navigate('/results', { state: { uploadId: id } });
          return;
        }
      } catch (error) {
        console.error('Error polling PDF:', error);
      }
      
      if (pdfPolls >= maxPolls) {
        clearInterval(pdfPolling);
      }
    }, 10000);
    
    // Store references for cleanup
    pollTimeoutRef.current = { imagePolling, pdfPolling };
  };


  return (
    <div className="demo">
      <div className="container">
        <motion.div 
          className="demo-header"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h1>AI Startup Analysis Demo</h1>
          <p>Experience our AI-powered startup analysis with normal or custom data</p>
        </motion.div>

        <motion.div 
          className="demo-tabs"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <button 
            className={`tab-button ${activeTab === 'normal' ? 'active' : ''}`}
            onClick={() => setActiveTab('normal')}
          >
            Normal Demo
          </button>
          <button 
            className={`tab-button ${activeTab === 'custom' ? 'active' : ''}`}
            onClick={() => setActiveTab('custom')}
          >
            Custom Demo
          </button>
        </motion.div>

        <div className="demo-content">
          {activeTab === 'normal' ? (
            <motion.div 
              className="normal-demo"
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
            >
              <div className="demo-section">
                <h2>Normal Demo</h2>
                <p>Experience our analysis with pre-selected startup data</p>
                
                <div className="input-group">
                  <label>Startup Name</label>
                  <input 
                    type="text" 
                    value={normalStartupName} 
                    disabled 
                    className="input-field disabled"
                  />
                </div>

                <div className="input-group">
                  <label>Data File</label>
                  <div className="file-display">
                    <div className="file-icon">📦</div>
                    <div className="file-info">
                      <span className="file-name">{normalZipFile.name}</span>
                      <span className="file-size">{normalZipFile.size}</span>
                    </div>
                    <span className="file-status">Pre-selected</span>
                  </div>
                </div>
              </div>
            </motion.div>
          ) : (
            <motion.div 
              className="custom-demo"
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
            >
              <div className="demo-section">
                <h2>Custom Demo</h2>
                <p>Upload your own startup data for analysis</p>
                
                <div className="input-group">
                  <label>Startup Name *</label>
                  <input 
                    type="text" 
                    value={customStartupName}
                    onChange={(e) => setCustomStartupName(e.target.value)}
                    placeholder="Enter startup name"
                    className="input-field"
                  />
                </div>

                <div className="input-group">
                  <label>Upload ZIP File *</label>
                  <div className="file-upload-area">
                    <input 
                      type="file"
                      ref={fileInputRef}
                      accept=".zip"
                      onChange={handleFileChange}
                      className="file-input"
                    />
                    <div 
                      className="file-upload-display"
                      onClick={() => fileInputRef.current?.click()}
                    >
                      {customFile ? (
                        <div className="file-selected">
                          <div className="file-icon">📦</div>
                          <div className="file-info">
                            <span className="file-name">{customFile.name}</span>
                            <span className="file-size">
                              {(customFile.size / (1024 * 1024)).toFixed(2)} MB
                            </span>
                          </div>
                        </div>
                      ) : (
                        <div className="file-placeholder">
                          <div className="upload-icon">📁</div>
                          <span>Click to select ZIP file</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          <motion.div 
            className="upload-section"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            {error && (
              <motion.div 
                className="error-message"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <div className="error-icon">⚠️</div>
                <p>{error}</p>
                <button 
                  className="btn retry-btn"
                  onClick={() => {
                    setError(null);
                    setUploadComplete(false);
                    setUploadProgress(0);
                    setIsCountingDown(false);
                    setPollingStarted(false);
                    setCountdown(300);
                    
                    // Cancel any ongoing polling
                    if (pollTimeoutRef.current) {
                      clearInterval(pollTimeoutRef.current.imagePolling);
                      clearInterval(pollTimeoutRef.current.pdfPolling);
                      pollTimeoutRef.current = null;
                    }
                  }}
                >
                  Try Again
                </button>
              </motion.div>
            )}
            
            {!uploadComplete && !error ? (
              <div className="upload-area">
                <button 
                  className="btn upload-btn" 
                  onClick={handleUpload}
                  disabled={isUploading}
                >
                  {isUploading ? 'Uploading...' : 'Upload'}
                </button>
                
                {isUploading && (
                  <motion.div 
                    className="progress-container"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className="progress-bar">
                      <motion.div 
                        className="progress-fill"
                        initial={{ width: 0 }}
                        animate={{ width: `${uploadProgress}%` }}
                        transition={{ duration: 0.3 }}
                      />
                    </div>
                    <span className="progress-text">{Math.round(uploadProgress)}%</span>
                  </motion.div>
                )}
              </div>
            ) : (
              <div className="upload-success">
                <motion.div 
                  className="success-icon"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 200 }}
                >
                  ✅
                </motion.div>
                <p>Files uploaded successfully!</p>
                
                {uploadId && (
                  <div className="upload-info">
                    <p className="upload-id">Upload ID: {uploadId}</p>
                  </div>
                )}
                
                {isCountingDown && (
                  <motion.div 
                    className="countdown-progress"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                  >
                    <div className="countdown-icon">⏱️</div>
                    <h3>Preparing Analysis</h3>
                    <p>Processing will begin in:</p>
                    <div className="countdown-timer">
                      {formatTime(countdown)}
                    </div>
                    <div className="countdown-bar">
                      <motion.div 
                        className="countdown-fill"
                        initial={{ width: "100%" }}
                        animate={{ width: `${(countdown / 300) * 100}%` }}
                        transition={{ duration: 1 }}
                      />
                    </div>
                    <span className="countdown-note">
                      Files uploaded successfully. Background processing has started...
                    </span>
                  </motion.div>
                )}
                
                {isProcessing && (
                  <motion.div 
                    className="generation-progress"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                  >
                    <div className="spinner"></div>
                    <p>Processing your data...</p>
                    <div className="timer">
                      Time elapsed: {formatTime(processingTimer)}
                    </div>
                    <span className="analysis-note">
                      Redirecting to results page and starting API polling...
                    </span>
                  </motion.div>
                )}
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Demo;
