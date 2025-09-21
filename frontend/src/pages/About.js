import React from 'react';
import { motion } from 'framer-motion';
import './About.css';
import boyAvatar from "../assets/boy.jpg";
import boyAvatar1 from "../assets/boy1.jpg";
import boyAvatar2 from "../assets/boy2.jpg";
import boyAvatar3 from "../assets/boy3.jpg";
import girlAvatar from "../assets/girl.jpg";

const About = () => {
  const developers = [
    {
      name: "Rishi Ketu Chand",
      role: "Software Developer",
      
      image: boyAvatar,
      skills: ["Deep Learning", "NLP", "Computer Vision"],
      github: "alexchen",
      linkedin: "alex-chen-ai"
    },
    {
      name: "Prashant Kumar",
      role: "Senior Software Developer",
      
      image: boyAvatar1,
      skills: ["React", "Node.js", "AWS"],
      github: "sarahj",
      linkedin: "sarah-johnson-dev"
    },
    {
      name: "Ram Tiwari",
      role: "Senior Software Developer",
      
      image: boyAvatar2,
      skills: ["Python", "Financial Modeling", "Statistics"],
      github: "marcusr",
      linkedin: "marcus-rodriguez-data"
    },
    {
      name: "Sohan S P",
      role: "Software Developer",
      
      image: boyAvatar3,
      skills: ["UI/UX", "Figma", "Data Visualization"],
      github: "emilyw",
      linkedin: "emily-watson-design"
    },
    {
      name: "Rashmi Hegde",
      role: "Software Developer",
      
      image: girlAvatar,
      skills: ["Kubernetes", "Docker", "CI/CD"],
      github: "davidkim",
      linkedin: "david-kim-devops"
    }
  ];

  return (
    <div className="about">
      <div className="container">
        <motion.div 
          className="about-header"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h1>Meet Our Team</h1>
          <p>The brilliant minds behind our AI-powered investment analysis platform</p>
        </motion.div>

        <motion.div 
          className="mission-section"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <div className="mission-content">
            <h2>Our Mission</h2>
            <p>
              We're on a mission to democratize investment analysis by leveraging cutting-edge AI technology. 
              Our team combines deep expertise in artificial intelligence, finance, and user experience to 
              create tools that save investors time while providing comprehensive, accurate insights.We understand the challenges faced by modern investors and are committed to solving them through innovative technology.
            </p>
            <p>
              
            </p>
          </div>
        </motion.div>

        <div className="team-section">
          <motion.h2 
            className="team-title"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            Our Team
          </motion.h2>
          
          <div className="developers-grid">
            {developers.map((developer, index) => (
              <motion.div 
                key={index}
                className="developer-card"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.6 + index * 0.1 }}
                whileHover={{ y: -10 }}
              >
                <div className="developer-image">
                  <img src={developer.image} alt={developer.name} />
                  <div className="image-overlay">
                    <div className="social-links">
                      <a 
                        href={`https://github.com/${developer.github}`} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="social-link"
                      >
                        <svg viewBox="0 0 24 24" width="20" height="20">
                          <path fill="currentColor" d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.17 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.604-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.464-1.11-1.464-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.167 22 16.418 22 12c0-5.523-4.477-10-10-10z"/>
                        </svg>
                      </a>
                      <a 
                        href={`https://linkedin.com/in/${developer.linkedin}`} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="social-link"
                      >
                        <svg viewBox="0 0 24 24" width="20" height="20">
                          <path fill="currentColor" d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                        </svg>
                      </a>
                    </div>
                  </div>
                </div>
                
                <div className="developer-info">
                  <h3>{developer.name}</h3>
                  <p className="role">{developer.role}</p>
                  
                  
                  <div className="skills">
                    {developer.skills.map((skill, skillIndex) => (
                      <span key={skillIndex} className="skill-tag">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        <motion.div 
          className="values-section"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <h2>Our Values</h2>
          <div className="values-grid">
            <div className="value-item">
              <div className="value-icon">🎯</div>
              <h3>Precision</h3>
              <p>We deliver accurate, reliable analysis that investors can trust for critical decisions.</p>
            </div>
            <div className="value-item">
              <div className="value-icon">⚡</div>
              <h3>Speed</h3>
              <p>Our AI-powered platform delivers comprehensive insights in minutes, not days.</p>
            </div>
            <div className="value-item">
              <div className="value-icon">🔒</div>
              <h3>Security</h3>
              <p>We prioritize data security and privacy with enterprise-grade protection.</p>
            </div>
            <div className="value-item">
              <div className="value-icon">🌟</div>
              <h3>Innovation</h3>
              <p>We continuously push the boundaries of what's possible with AI and data analysis.</p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default About;
