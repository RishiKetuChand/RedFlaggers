import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import './Home.css';

const Home = () => {
  const features = [
    {
      title: "AI-Powered Analysis",
      description: "Advanced machine learning algorithms analyze startup data to provide comprehensive insights",
      icon: "🤖"
    },
    {
      title: "Time-Saving Reports",
      description: "Get detailed analysis reports in minutes, not hours or days",
      icon: "⚡"
    },
    {
      title: "Document Processing",
      description: "Upload PDFs, financial statements, and business plans for automated analysis",
      icon: "📄"
    },
    {
      title: "Investment Insights",
      description: "Receive actionable investment recommendations based on comprehensive data analysis",
      icon: "💡"
    },
    {
      title: "Risk Assessment",
      description: "Identify potential risks and opportunities with our advanced risk analysis engine",
      icon: "📊"
    },
    {
      title: "Real-time Processing",
      description: "Monitor analysis progress in real-time with live updates and notifications",
      icon: "🔄"
    }
  ];

  return (
    <div className="home">
      <section className="hero">
        <div className="container">
          <motion.div 
            className="hero-content"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.2 }}
          >
            <h1 className="hero-title">
              Revolutionize Your <span className="gradient-text">Investment Decisions</span>
            </h1>
            <p className="hero-subtitle">
              Save precious time with our AI-powered startup analysis platform. 
              Get comprehensive insights and investment recommendations in minutes.
            </p>
            <div className="hero-buttons">
              <Link to="/demo" className="btn">
                Try Demo
              </Link>
              <a href="#features" className="btn btn-secondary">
                Learn More
              </a>
            </div>
          </motion.div>
          
          <motion.div 
            className="hero-visual"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 1, delay: 0.5 }}
          >
            <div className="floating-card">
              <div className="card-header">
                <div className="card-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span>Analysis Report</span>
              </div>
              <div className="card-content">
                <div className="metric">
                  <span className="metric-label">Risk Score</span>
                  <span className="metric-value">7.2/10</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Market Potential</span>
                  <span className="metric-value">High</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Recommendation</span>
                  <span className="metric-value positive">Invest</span>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      <section id="features" className="features">
        <div className="container">
          <motion.div 
            className="section-header"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <h2>Powerful Features for Smart Investors</h2>
            <p>Everything you need to make informed investment decisions</p>
          </motion.div>
          
          <div className="features-grid">
            {features.map((feature, index) => (
              <motion.div 
                key={index}
                className="feature-card"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                whileHover={{ y: -5 }}
              >
                <div className="feature-icon">{feature.icon}</div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section className="cta">
        <div className="container">
          <motion.div 
            className="cta-content"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <h2>Ready to Transform Your Investment Process?</h2>
            <p>Join leading investors who trust our AI-powered analysis platform</p>
            <Link to="/demo" className="btn">
              Start Free Demo
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default Home;