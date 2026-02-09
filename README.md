Simulation & Data: Cisco Packet Tracer, Kali Linux (hping3, Nmap)
AI & Machine Learning: Python, Scikit-learn, Pandas & NumPy, Flask / FastAPI
Development & Response: Java
DevOps & Infrastructure: GitHub, Docker
Security & Cryptography: SHA-256
Full Dashboard Tech Stack: React, MongoDB, Node.js, Express, Socket.ioVAJRA: AI-Powered Defence Cybersecurity System ⚡🛡️
VAJRA is an integrated cybersecurity framework designed to detect, analyze, and autonomously respond to network-level threats. By combining Artificial Intelligence, Real-time Monitoring, and DevOps automation, the system provides a proactive shield against evolving cyber attacks.

🚀 Overview
The project simulates a high-stakes network environment where the VAJRA "Brain" analyzes incoming traffic to identify malicious patterns such as IP Spoofing, DDoS attacks, and Network Jamming. Once a threat is identified, an automated response system triggers defensive measures to secure the network.

🛠️ Tech Stack
Simulation & Data
Cisco Packet Tracer: Network topology design and traffic generation.

Kali Linux: Threat simulation (hping3, Nmap).

Wireshark: Deep packet inspection and data labeling.

Intelligence (The Brain)
Python: Core ML development.

Scikit-learn: Classification models (Random Forest/SVM).

Pandas & NumPy: Feature engineering and data processing.

Core System & Response
C++: High-performance real-time traffic monitoring.

Java: Backend logic for threat mitigation and response management.

SHA-256: Cryptographic integrity for system logs.

Dashboard & Monitoring (MERN)
React: Modern, responsive frontend for real-time visualization.

MongoDB: NoSQL database for flexible threat logging and attack history.

Node.js & Express: Backend API services.

Socket.io: Real-time alert broadcasting to the dashboard.

DevOps & Infrastructure
GitHub: Version control and source code management.

GitHub Actions: CI/CD pipeline for automated testing and builds.

Docker: Containerization of AI and Dashboard services.

Kubernetes: Orchestration for deploying the simulation cluster.

🏗️ System Architecture
Traffic Capture: Network data is generated in Packet Tracer and captured for analysis.

Preprocessing: Raw packets are converted into numerical features using Python.

Inference: The VAJRA AI model classifies traffic as Normal or Threat.

Action: The C++/Java service executes a response (e.g., blocking an IP via firewall rules).

Visualization: The React dashboard displays live metrics and attack history stored in MongoDB.

📁 Project Structure
Plaintext
├── src/
│   ├── vajra_ai/           # Python ML models and scripts
│   ├── core_monitor/       # C++ Real-time monitoring service
│   ├── response_manager/   # Java mitigation logic
│   ├── dashboard_web/      # React Frontend (VAJRA UI)
│   └── dashboard_api/      # Node.js/Express & MongoDB backend
├── simulation/             # Packet Tracer files and Kali scripts
├── deployment/             # Dockerfiles & Kubernetes manifests
└── docs/                   # Documentation and SHA-256 log samples
🛡️ Key Features
Indestructible Integrity: All threat logs are hashed using SHA-256 to prevent tampering.

Lightning Response: Reduces human response time to sub-millisecond levels.

MERN Dashboard: Real-time visualization of the network "battlefield."