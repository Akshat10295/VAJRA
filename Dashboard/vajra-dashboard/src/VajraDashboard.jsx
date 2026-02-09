import React, { useState, useEffect } from 'react';
import { Shield, AlertTriangle, Activity, Zap, Eye, TrendingUp, Server, Clock, CheckCircle, XCircle, Play } from 'lucide-react';

// Import the stylesheet
import './VajraDashboard.css';

export default function VajraDashboard() {
  const [threats, setThreats] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [mitigationLog, setMitigationLog] = useState([]);
  const [metrics, setMetrics] = useState({
    threatsStopped: 0,
    uptime: 100,
    avgResponseTime: 0,
    activeConnections: 1250
  });
  const [isMonitoring, setIsMonitoring] = useState(true);

  // ... (Your simulation logic remains exactly the same) ...
  const simulateAttack = (attackType, severity) => {
    const sources = ['185.220.101.', '192.168.50.', '10.0.0.', '172.16.', '203.0.113.'];
    const randomSource = sources[Math.floor(Math.random() * sources.length)] + Math.floor(Math.random() * 255);
    
    const newThreat = {
      id: Date.now(),
      type: attackType,
      severity: severity,
      source: randomSource,
      status: 'active',
      time: new Date().toLocaleTimeString(),
      detected: Date.now()
    };

    setThreats(prev => [newThreat, ...prev.slice(0, 9)]);

    // AI predicts next possible attack
    setTimeout(() => {
      predictNextAttack(attackType);
    }, 1000);

    // Auto-mitigation kicks in
    setTimeout(() => {
      mitigateThreat(newThreat);
    }, 2000 + Math.random() * 1000);

    // Increase connection spike during attack
    setMetrics(prev => ({
      ...prev,
      activeConnections: prev.activeConnections + Math.floor(Math.random() * 5000)
    }));
  };

  const predictNextAttack = (currentAttack) => {
    const attackTypes = ['Volumetric DDoS', 'SYN Flood', 'HTTP Flood', 'UDP Flood', 'DNS Amplification'];
    const targets = ['API Gateway', 'Load Balancer', 'Web Server', 'Database', 'CDN'];
    
    const prediction = {
      id: Date.now(),
      time: new Date(Date.now() + Math.random() * 600000).toLocaleTimeString(),
      probability: Math.floor(60 + Math.random() * 35),
      type: attackTypes[Math.floor(Math.random() * attackTypes.length)],
      target: targets[Math.floor(Math.random() * targets.length)]
    };

    setPredictions(prev => [prediction, ...prev.slice(0, 2)]);
  };

  const mitigateThreat = (threat) => {
    const actions = [
      'Rate limiting enabled',
      'IP blacklist updated',
      'Traffic rerouted to WAF',
      'CDN cache purged',
      'Firewall rules applied',
      'Load balancer reconfigured'
    ];

    const action = actions[Math.floor(Math.random() * actions.length)];
    const responseTime = (Math.random() * 0.5 + 0.1).toFixed(2);

    // Update threat status
    setThreats(prev => 
      prev.map(t => t.id === threat.id ? { ...t, status: 'mitigated' } : t)
    );

    // Log mitigation
    setMitigationLog(prev => [{
      action: action,
      time: new Date().toLocaleTimeString(),
      status: 'success',
      responseTime: responseTime
    }, ...prev.slice(0, 7)]);

    // Update metrics
    setMetrics(prev => ({
      ...prev,
      threatsStopped: prev.threatsStopped + 1,
      avgResponseTime: ((prev.avgResponseTime * prev.threatsStopped + parseFloat(responseTime)) / (prev.threatsStopped + 1)).toFixed(2),
      activeConnections: Math.max(1250, prev.activeConnections - Math.floor(Math.random() * 3000))
    }));
  };

  // Random connection fluctuations
  useEffect(() => {
    if (!isMonitoring) return;
    
    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        activeConnections: Math.max(500, prev.activeConnections + Math.floor(Math.random() * 200 - 100))
      }));
    }, 3000);
    return () => clearInterval(interval);
  }, [isMonitoring]);

  return (
    <div className="vajra-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div className="header-content">
          <div className="header-title-group">
            <div className="header-icon-wrapper">
              <Shield width={32} height={32} />
            </div>
            <div>
              <h1 className="header-title">
                VAJRA
              </h1>
              <p className="header-subtitle">AI-Powered Defense Agent System</p>
            </div>
          </div>
          <div className="header-status-group">
            <div className="status-badge">
              <div className="status-dot-pulse"></div>
              <span>System Active</span>
            </div>
          </div>
        </div>
      </div>

      {/* Attack Simulation Controls */}
      <div className="card simulation-controls">
        <h2 className="card-title">
          <Play width={20} height={20} style={{ color: '#22d3ee' }} />
          Simulate Incoming Attack
        </h2>
        <div className="simulation-buttons">
          <button
            onClick={() => simulateAttack('DDoS', 'critical')}
            className="sim-button sim-button-ddos"
          >
            DDoS Attack (Critical)
          </button>
          <button
            onClick={() => simulateAttack('SYN Flood', 'high')}
            className="sim-button sim-button-syn"
          >
            SYN Flood (High)
          </button>
          <button
            onClick={() => simulateAttack('HTTP Flood', 'medium')}
            className="sim-button sim-button-http"
          >
            HTTP Flood (Medium)
          </button>
          <button
            onClick={() => simulateAttack('Port Scan', 'low')}
            className="sim-button sim-button-scan"
          >
            Port Scan (Low)
          </button>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-title">Threats Mitigated</span>
            <CheckCircle width={20} height={20} className="metric-icon-green" />
          </div>
          <div className="metric-value metric-value-green">{metrics.threatsStopped}</div>
          <div className="metric-description">Since session started</div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-title">System Uptime</span>
            <Activity width={20} height={20} className="metric-icon-cyan" />
          </div>
          <div className="metric-value metric-value-cyan">{metrics.uptime}%</div>
          <div className="metric-description">Operational status</div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-title">Avg Response</span>
            <Zap width={20} height={20} className="metric-icon-yellow" />
          </div>
          <div className="metric-value metric-value-yellow">{metrics.avgResponseTime || 0}s</div>
          <div className="metric-description">Mitigation time</div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-title">Active Connections</span>
            <Server width={20} height={20} className="metric-icon-blue" />
          </div>
          <div className="metric-value metric-value-blue">{metrics.activeConnections.toLocaleString()}</div>
          <div className="metric-description">Real-time monitoring</div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="main-content-grid">
        {/* Live Threat Detection */}
        <div className="card threat-detection-panel">
          <div className="card-header">
            <h2 className="card-title">
              <Eye width={20} height={20} style={{ color: '#f87171' }} />
              Live Threat Detection
            </h2>
            <div className="scanning-indicator">
              <div className="scanning-dot-pulse"></div>
              <span>Scanning</span>
            </div>
          </div>
          <div className="threat-list">
            {threats.length === 0 ? (
              <div className="threat-list-empty">
                <Shield width={48} height={48} />
                <p>No threats detected. System monitoring...</p>
                <p>Simulate an attack to see AI detection in action</p>
              </div>
            ) : (
              threats.map(threat => (
                <div
                  key={threat.id}
                  className={`threat-item ${threat.status === 'active' ? 'active' : 'mitigated'}`}
                >
                  <div className="threat-item-content">
                    <div className="threat-info-group">
                      <AlertTriangle
                        width={20}
                        height={20}
                        className={`threat-icon severity-${threat.severity}`}
                      />
                      <div>
                        <div className="threat-type">{threat.type} Attack</div>
                        <div className="threat-details">
                          Source: {threat.source} • {threat.time}
                        </div>
                      </div>
                    </div>
                    <div className="threat-badge-group">
                      <span
                        className={`threat-badge severity-badge severity-${threat.severity}`}
                      >
                        {threat.severity}
                      </span>
                      <span
                        className={`threat-badge status-badge status-${threat.status}`}
                      >
                        {threat.status}
                      </span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* AI Predictions */}
        <div className="card ai-predictions-panel">
          <h2 className="card-title">
            <TrendingUp width={20} height={20} style={{ color: '#c084fc' }} />
            AI Predictions
          </h2>
          <div className="prediction-list">
            {predictions.length === 0 ? (
              <div className="prediction-list-empty">
                <TrendingUp width={40} height={40} />
                <p>Awaiting data to predict...</p>
              </div>
            ) : (
              predictions.map((pred) => (
                <div key={pred.id} className="prediction-item">
                  <div className="prediction-header">
                    <span className="prediction-time">{pred.time}</span>
                    <span className="prediction-probability">
                      {pred.probability}% likely
                    </span>
                  </div>
                  <div className="prediction-type">{pred.type}</div>
                  <div className="prediction-target">Target: {pred.target}</div>
                  <div className="prediction-bar-container">
                    <div
                      className="prediction-bar"
                      style={{ width: `${pred.probability}%` }}
                    ></div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Auto-Mitigation Actions */}
        <div className="card mitigation-log-panel">
          <h2 className="card-title">
            <Zap width={20} height={20} style={{ color: '#22d3ee' }} />
            Automated Mitigation Log
          </h2>
          {mitigationLog.length === 0 ? (
            <div className="mitigation-log-empty">
              <Zap width={40} height={40} />
              <p>No mitigation actions yet</p>
            </div>
          ) : (
            <div className="mitigation-log-grid">
              {mitigationLog.map((action, idx) => (
                <div key={idx} className="mitigation-item">
                  <div className="mitigation-item-header">
                    <CheckCircle width={16} height={16} style={{ color: '#4ade80' }} />
                    <span>{action.time}</span>
                  </div>
                  <div className="mitigation-item-action">{action.action}</div>
                  <div className="mitigation-item-response">⚡ {action.responseTime}s</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Footer Stats */}
      <div className="dashboard-footer">
        <div>Powered by AI/ML • DevOps Integration Active</div>
        <div>Version 1.0.0 • Monitoring: {isMonitoring ? 'Active' : 'Paused'}</div>
      </div>
    </div>
  );
}