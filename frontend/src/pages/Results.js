import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Pagination, Autoplay } from 'swiper/modules';
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';
import './Results.css';

const Results = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [activeTab, setActiveTab] = useState('images');
  const [images, setImages] = useState([]);
  const [pdfData, setPdfData] = useState(null);
  const [isLoadingImages, setIsLoadingImages] = useState(true);
  const [isLoadingPdf, setIsLoadingPdf] = useState(true);
  const [pollingCount, setPollingCount] = useState(0);
  const [uploadId, setUploadId] = useState(null);
  const [error, setError] = useState(null);
  const [imageError, setImageError] = useState(null);
  const [pdfError, setPdfError] = useState(null);
  const [processingTime, setProcessingTime] = useState(0);
  const imagePollingRef = useRef(null);
  const pdfPollingRef = useRef(null);
  const processingTimerRef = useRef(null);

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
  useEffect(() => {
    const id = location.state?.uploadId;
    if (!id) {
      navigate('/demo');
      return;
    }
    
    setUploadId(id);
    pollImageAPI(id);
    pollPdfAPI(id);
    
    // Start processing timer
    processingTimerRef.current = setInterval(() => {
      setProcessingTime(prev => prev + 1);
    }, 1000);

    return () => {
      if (processingTimerRef.current) {
        clearInterval(processingTimerRef.current);
        processingTimerRef.current = null;
      }
      if (imagePollingRef.current) {
        clearTimeout(imagePollingRef.current);
        imagePollingRef.current = null;
      }
      if (pdfPollingRef.current) {
        clearTimeout(pdfPollingRef.current);
        pdfPollingRef.current = null;
      }
    };
  }, [location.state, navigate]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

// Replace your pollImageAPI with this
const pollImageAPI = (id) => {
  const maxPolls = 180;
  let polls = 0;

  const tick = async () => {
    polls += 1;
    setPollingCount(polls);

    try {
      const { data } = await axios.get(`${API_BASE_URL}/status/images`, {
        params: { upload_id: id },
      });

      if (data?.status === 'completed') {
        // Use URLs if present; otherwise trust 'completed' and set empty array (or do a one-shot refetch)
        const processedImages = (data.download_url || []).map((url, index) => ({
          id: index + 1,
          url,
          title: getImageTitle(index),
          description: getImageDescription(index),
        }));
        // Stop polling immediately
        if (imagePollingRef.current) {
          clearTimeout(imagePollingRef.current);
          imagePollingRef.current = null;
        }
        setImages(processedImages);
        setIsLoadingImages(false);
        return;
      }

      if (data?.status === 'failed') {
        if (imagePollingRef.current) {
          clearTimeout(imagePollingRef.current);
          imagePollingRef.current = null;
        }
        setImageError('Image generation failed. Please try uploading again or contact support.');
        setIsLoadingImages(false);
        return;
      }
    } catch (err) {
      console.error('Error polling image API:', err);
      if (polls > 5) setImageError('Failed to check image status. Network connection issue.');
    }

    if (polls >= maxPolls) {
      if (imagePollingRef.current) {
        clearTimeout(imagePollingRef.current);
        imagePollingRef.current = null;
      }
      setIsLoadingImages(false);
      setImageError('Image generation timed out after 30 minutes. Please try again.');
      return;
    }

    // schedule next tick
    imagePollingRef.current = setTimeout(tick, 10000);
  };

  // kick off
  imagePollingRef.current = setTimeout(tick, 0);
};

// Replace your pollPdfAPI with this
const pollPdfAPI = (id) => {
  const maxPolls = 180;
  let polls = 0;

  const tick = async () => {
    polls += 1;

    try {
      const { data } = await axios.get(`${API_BASE_URL}/status/pdf`, {
        params: { upload_id: id },
      });

      if (data?.status === 'completed') {
        setPdfData({
          url: data.download_url || null,
          filename: data.filename || 'report.pdf',
          pages: data.pages || 'N/A',
          size: data.size || 'N/A',
          generatedAt: new Date().toISOString(),
        });
        if (pdfPollingRef.current) {
          clearTimeout(pdfPollingRef.current);
          pdfPollingRef.current = null;
        }
        setIsLoadingPdf(false);
        return;
      }

      if (data?.status === 'failed') {
        if (pdfPollingRef.current) {
          clearTimeout(pdfPollingRef.current);
          pdfPollingRef.current = null;
        }
        setPdfError('PDF report generation failed. Please try uploading again or contact support.');
        setIsLoadingPdf(false);
        return;
      }
    } catch (err) {
      console.error('Error polling PDF API:', err);
      if (polls > 5) setPdfError('Failed to check PDF status. Network connection issue.');
    }

    if (polls >= maxPolls) {
      if (pdfPollingRef.current) {
        clearTimeout(pdfPollingRef.current);
        pdfPollingRef.current = null;
      }
      setIsLoadingPdf(false);
      setPdfError('PDF generation timed out after 30 minutes. Please try again.');
      return;
    }

    pdfPollingRef.current = setTimeout(tick, 10000);
  };

  pdfPollingRef.current = setTimeout(tick, 0);
};

  const getImageTitle = (index) => {
    const titles = [
      'Front Page - Name of the start up',
      'Product Details',
      'Financial Metrics',
      'Product Roadmap',
      'Risk Assessment',
      'Investment Metrics'
    ];
    return titles[index] || `Analysis Chart ${index + 1}`;
  };

  const getImageDescription = (index) => {
    const descriptions = [
      'Title page representing start up name and team name',
      'Brief notes about the problem and solution',
      'Financial forecast and growth trajectory',
      'Organizational hierarchy and key personnel',
      'Development timeline and feature releases',
      'Risk factors analysis and mitigation strategies',
      'Key performance indicators and ROI analysis'
    ];
    return descriptions[index] || `Detailed analysis visualization ${index + 1}`;
  };

  const handleDownloadPdf = () => {
    if (pdfData) {
      const link = document.createElement('a');
      link.href = pdfData.url;
      link.download = pdfData.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleBackToDemo = () => {
    // Clean up all polling before navigating
  if (processingTimerRef.current) {
    clearInterval(processingTimerRef.current);
    processingTimerRef.current = null;
  }
  if (imagePollingRef.current) {
    clearTimeout(imagePollingRef.current);
    imagePollingRef.current = null;
  }
  if (pdfPollingRef.current) {
    clearTimeout(pdfPollingRef.current);
    pdfPollingRef.current = null;
  }
    navigate('/demo');
  };

  return (
    <div className="results">
      <div className="container">
        <motion.div 
          className="results-header"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h1>Analysis Results</h1>
          <p>Your AI-powered startup analysis is ready</p>
          <div className="header-controls">
            <div className="processing-info">
              <span className="processing-time">Processing Time: {formatTime(processingTime)}</span>
              <span className="estimated-time">Est. Total: 30 min</span>
            </div>
            <button 
              className="btn back-btn"
              onClick={handleBackToDemo}
            >
              ← Back to Demo
            </button>
          </div>
        </motion.div>

        <div className="results-content">
          {error && (
            <motion.div 
              className="error-section"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <div className="error-card">
                <div className="error-icon">⚠️</div>
                <h3>Processing Error</h3>
                <p>{error}</p>
                <button 
                  className="btn back-btn"
                  onClick={() => navigate('/demo')}
                >
                  Back to Demo
                </button>
              </div>
            </motion.div>
          )}

          {uploadId && (
            <motion.div 
              className="upload-info-section"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <p className="upload-id-display">Processing Upload ID: <span>{uploadId}</span></p>
            </motion.div>
          )}

          {/* Tab Navigation */}
          <motion.div 
            className="results-tabs"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <button 
              className={`tab-button ${activeTab === 'images' ? 'active' : ''}`}
              onClick={() => setActiveTab('images')}
            >
              📊 Visual Analysis
              {isLoadingImages && <div className="tab-loading-dot"></div>}
            </button>
            <button 
              className={`tab-button ${activeTab === 'pdf' ? 'active' : ''}`}
              onClick={() => setActiveTab('pdf')}
            >
              📄 Detailed Report
              {isLoadingPdf && <div className="tab-loading-dot"></div>}
            </button>
          </motion.div>

          {/* Tab Content */}
          <div className="tab-content">
            {activeTab === 'images' && (
              <motion.div 
                className="images-section"
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8 }}
              >
                <div className="section-header">
                  <h2>📊 Visual Analysis</h2>
                  {isLoadingImages && (
                    <div className="loading-indicator">
                      <div className="spinner small"></div>
                      <span>Loading images... (Poll #{pollingCount}/180)</span>
                    </div>
                  )}
                </div>

                {imageError ? (
                  <motion.div 
                    className="section-error"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                  >
                    <div className="error-card">
                      <div className="error-icon">❌</div>
                      <h3>Image Generation Failed</h3>
                      <p>{imageError}</p>
                      <button 
                        className="btn back-btn"
                        onClick={() => navigate('/demo')}
                      >
                        Back to Demo
                      </button>
                    </div>
                  </motion.div>
                ) : isLoadingImages ? (
                  <div className="loading-placeholder">
                    <div className="loading-message">
                      <div className="loading-icon">🔄</div>
                      <h3>Generating Visual Analysis</h3>
                      <p>Our AI is creating detailed charts and visualizations</p>
                      <div className="progress-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                      <p className="time-notice">This process can take up to 30 minutes</p>
                    </div>
                  </div>
                ) : (
                  <motion.div 
                    className="images-slider-container"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.8 }}
                  >
                    <Swiper
                      modules={[Navigation, Pagination, Autoplay]}
                      spaceBetween={30}
                      slidesPerView={1}
                      navigation
                      pagination={{ clickable: true }}
                      autoplay={{
                        delay: 5000,
                        disableOnInteraction: false,
                      }}
                      className="images-swiper"
                    >
                      {images.map((image, index) => (
                        <SwiperSlide key={image.id}>
                          <motion.div 
                            className="image-slide"
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                          >
                            <div className="image-container">
                              <img 
                                src={image.url}
                                alt={image.title}
                                className="result-image"
                                onError={(e) => {
                                  // Fallback to placeholder if image fails to load
                                  e.target.src = `https://via.placeholder.com/800x600/4f46e5/ffffff?text=${encodeURIComponent(image.title)}`;
                                }}
                              />
                            </div>
                            <div className="image-info">
                              <h3>{image.title}</h3>
                              <p>{image.description}</p>
                              <div className="image-meta">
                                <span>Image {index + 1} of {images.length}</span>
                              </div>
                            </div>
                          </motion.div>
                        </SwiperSlide>
                      ))}
                    </Swiper>
                  </motion.div>
                )}
              </motion.div>
            )}

            {activeTab === 'pdf' && (
              <motion.div 
                className="pdf-section"
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8 }}
              >
                <div className="section-header">
                  <h2>📄 Detailed Report</h2>
                  {isLoadingPdf && (
                    <div className="loading-indicator">
                      <div className="spinner small"></div>
                      <span>Generating PDF report...</span>
                    </div>
                  )}
                </div>

                {pdfError ? (
                  <motion.div 
                    className="section-error"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                  >
                    <div className="error-card">
                      <div className="error-icon">❌</div>
                      <h3>PDF Generation Failed</h3>
                      <p>{pdfError}</p>
                      <button 
                        className="btn back-btn"
                        onClick={() => navigate('/demo')}
                      >
                        Back to Demo
                      </button>
                    </div>
                  </motion.div>
                ) : isLoadingPdf ? (
                  <div className="pdf-loading">
                    <div className="pdf-placeholder">
                      <div className="pdf-icon">📄</div>
                      <div className="loading-text">
                        <h3>Analysis in Progress</h3>
                        <p>Our AI is generating your comprehensive startup analysis report</p>
                        <div className="progress-dots">
                          <span></span>
                          <span></span>
                          <span></span>
                        </div>
                        <p className="time-notice">This process can take up to 30 minutes</p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <motion.div 
                    className="pdf-ready"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.8 }}
                  >
                    <div className="pdf-card">
                      <div className="pdf-icon-large">📄</div>
                      <div className="pdf-details">
                        <h3>Startup Analysis Report</h3>
                        <p>Comprehensive AI-generated analysis</p>
                        <div className="pdf-meta">
                          <span>Pages: {pdfData?.pages}</span>
                          <span>Size: {pdfData?.size}</span>
                          <span>Generated: {new Date(pdfData?.generatedAt).toLocaleDateString()}</span>
                        </div>
                      </div>
                      <button 
                        className="btn download-pdf-btn"
                        onClick={handleDownloadPdf}
                      >
                        Download PDF
                      </button>
                    </div>
                  </motion.div>
                )}
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Results;
