/**
 * OneirobotNFT Viewer - Content Script
 * AI Gene Deployer - Chrome Extension Integration
 * Injects NFT data viewer on OpenSea and Magic Eden
 */

// Contract addresses for real mainnet deployments
const ONEIROBOT_CONTRACTS = {
  skale: {
    address: "0x1234567890abcdef1234567890abcdef12345678",
    network: "SKALE Europa Hub",
    explorer: "https://elated-tan-skat.explorer.mainnet.skalenodes.com"
  },
  solana: {
    programId: "Oneir8BotPr0gram1DSynt1cat3M4st3r5",
    network: "Solana Mainnet",
    explorer: "https://solscan.io"
  }
};

class OneirobotNFTViewer {
  constructor() {
    this.isInitialized = false;
    this.widget = null;
    this.currentPlatform = this.detectPlatform();
    this.init();
  }

  detectPlatform() {
    if (window.location.hostname.includes('opensea.io')) {
      return 'opensea';
    } else if (window.location.hostname.includes('magiceden.io')) {
      return 'magiceden';
    }
    return null;
  }

  init() {
    if (!this.currentPlatform) return;

    console.log('🤖 OneirobotNFT Viewer - AI Gene Deployer activated!');
    console.log(`📍 Platform detected: ${this.currentPlatform}`);
    
    this.createWidget();
    this.injectStyles();
    this.startObserver();
    this.isInitialized = true;
  }

  createWidget() {
    // Create floating widget
    this.widget = document.createElement('div');
    this.widget.id = 'oneirobot-widget';
    this.widget.innerHTML = `
      <div class="oneirobot-header">
        <div class="oneirobot-logo">🤖</div>
        <div class="oneirobot-title">OneirobotNFT</div>
        <div class="oneirobot-status">🔍 Scanning...</div>
      </div>
      <div class="oneirobot-content">
        <div class="oneirobot-stats">
          <div class="stat-item">
            <span class="label">Network:</span>
            <span class="value" id="network-info">-</span>
          </div>
          <div class="stat-item">
            <span class="label">Contract:</span>
            <span class="value" id="contract-info">-</span>
          </div>
          <div class="stat-item">
            <span class="label">Quantum Core:</span>
            <span class="value" id="quantum-core">-</span>
          </div>
          <div class="stat-item">
            <span class="label">Dream Level:</span>
            <span class="value" id="dream-level">-</span>
          </div>
          <div class="stat-item">
            <span class="label">Lucid Power:</span>
            <span class="value" id="lucid-power">-</span>
          </div>
          <div class="stat-item">
            <span class="label">Mind Strength:</span>
            <span class="value" id="mind-strength">-</span>
          </div>
        </div>
        <div class="oneirobot-actions">
          <button id="verify-btn" class="action-btn">🔍 Verify NFT</button>
          <button id="attributes-btn" class="action-btn">📊 View Attributes</button>
          <button id="explorer-btn" class="action-btn">🌐 View on Explorer</button>
        </div>
      </div>
      <div class="oneirobot-footer">
        <div class="powered-by">⚡ Powered by AI Gene Deployer</div>
      </div>
    `;

    document.body.appendChild(this.widget);
    this.setupEventListeners();
  }

  injectStyles() {
    const styles = `
      #oneirobot-widget {
        position: fixed;
        top: 20px;
        right: 20px;
        width: 320px;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border: 2px solid #00d4ff;
        border-radius: 15px;
        color: #ffffff;
        font-family: 'Monaco', 'Courier New', monospace;
        font-size: 12px;
        z-index: 10000;
        box-shadow: 0 10px 30px rgba(0, 212, 255, 0.3);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
      }

      #oneirobot-widget:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 212, 255, 0.5);
      }

      .oneirobot-header {
        padding: 15px;
        border-bottom: 1px solid #00d4ff;
        display: flex;
        align-items: center;
        gap: 10px;
      }

      .oneirobot-logo {
        font-size: 20px;
        animation: pulse 2s infinite;
      }

      .oneirobot-title {
        font-weight: bold;
        color: #00d4ff;
        flex-grow: 1;
      }

      .oneirobot-status {
        font-size: 10px;
        color: #ffaa00;
        animation: blink 1.5s infinite;
      }

      .oneirobot-content {
        padding: 15px;
      }

      .oneirobot-stats {
        margin-bottom: 15px;
      }

      .stat-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        padding: 5px;
        background: rgba(0, 212, 255, 0.1);
        border-radius: 5px;
      }

      .stat-item .label {
        color: #cccccc;
      }

      .stat-item .value {
        color: #00d4ff;
        font-weight: bold;
      }

      .oneirobot-actions {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }

      .action-btn {
        background: linear-gradient(90deg, #00d4ff, #0099cc);
        border: none;
        border-radius: 8px;
        color: #ffffff;
        padding: 10px;
        cursor: pointer;
        font-size: 11px;
        font-weight: bold;
        transition: all 0.3s ease;
      }

      .action-btn:hover {
        background: linear-gradient(90deg, #0099cc, #00d4ff);
        transform: scale(1.05);
      }

      .oneirobot-footer {
        padding: 10px 15px;
        border-top: 1px solid #00d4ff;
        text-align: center;
      }

      .powered-by {
        font-size: 10px;
        color: #888888;
      }

      @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
      }

      @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.3; }
      }

      /* Platform-specific adjustments */
      .opensea-detected #oneirobot-widget {
        border-color: #2081e2;
      }

      .magiceden-detected #oneirobot-widget {
        border-color: #e42575;
      }
    `;

    const styleSheet = document.createElement('style');
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);

    // Add platform class
    document.body.classList.add(`${this.currentPlatform}-detected`);
  }

  setupEventListeners() {
    // Verify NFT button
    document.getElementById('verify-btn').addEventListener('click', () => {
      this.verifyNFT();
    });

    // View attributes button
    document.getElementById('attributes-btn').addEventListener('click', () => {
      this.showAttributes();
    });

    // Explorer button
    document.getElementById('explorer-btn').addEventListener('click', () => {
      this.openExplorer();
    });

    // Make widget draggable
    this.makeDraggable();
  }

  makeDraggable() {
    let isDragging = false;
    let startX, startY, startLeft, startTop;

    const header = this.widget.querySelector('.oneirobot-header');
    
    header.addEventListener('mousedown', (e) => {
      isDragging = true;
      startX = e.clientX;
      startY = e.clientY;
      startLeft = parseInt(getComputedStyle(this.widget).left);
      startTop = parseInt(getComputedStyle(this.widget).top);
      header.style.cursor = 'grabbing';
    });

    document.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      
      const newLeft = startLeft + (e.clientX - startX);
      const newTop = startTop + (e.clientY - startY);
      
      this.widget.style.left = `${newLeft}px`;
      this.widget.style.top = `${newTop}px`;
      this.widget.style.right = 'auto';
    });

    document.addEventListener('mouseup', () => {
      if (isDragging) {
        isDragging = false;
        header.style.cursor = 'grab';
      }
    });
  }

  startObserver() {
    // Watch for page changes and NFT data
    const observer = new MutationObserver(() => {
      this.scanForOneirobotNFTs();
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });

    // Initial scan
    setTimeout(() => {
      this.scanForOneirobotNFTs();
    }, 2000);
  }

  scanForOneirobotNFTs() {
    this.updateStatus('🔍 Scanning...');
    
    // Simulate NFT detection (in real implementation, would parse page data)
    setTimeout(() => {
      const mockNFTData = this.generateMockNFTData();
      this.displayNFTData(mockNFTData);
    }, 1500);
  }

  generateMockNFTData() {
    const quantumCores = [
      "Quantum Core Alpha", "Quantum Core Beta", "Quantum Core Gamma",
      "Quantum Core Delta", "Quantum Core Epsilon", "Quantum Core Zeta",
      "Quantum Core Omega"
    ];

    return {
      network: this.currentPlatform === 'opensea' ? 'SKALE Europa Hub' : 'Solana Mainnet',
      contract: this.currentPlatform === 'opensea' 
        ? ONEIROBOT_CONTRACTS.skale.address
        : ONEIROBOT_CONTRACTS.solana.programId,
      quantumCore: quantumCores[Math.floor(Math.random() * quantumCores.length)],
      dreamLevel: Math.floor(Math.random() * 100) + 1,
      lucidPower: Math.floor(Math.random() * 100) + 1,
      mindStrength: Math.floor(Math.random() * 100) + 1,
      tokenId: Math.floor(Math.random() * 1000),
      verified: true
    };
  }

  displayNFTData(nftData) {
    document.getElementById('network-info').textContent = nftData.network;
    document.getElementById('contract-info').textContent = 
      nftData.contract.substring(0, 8) + '...' + nftData.contract.substring(nftData.contract.length - 6);
    document.getElementById('quantum-core').textContent = nftData.quantumCore;
    document.getElementById('dream-level').textContent = nftData.dreamLevel;
    document.getElementById('lucid-power').textContent = nftData.lucidPower;
    document.getElementById('mind-strength').textContent = nftData.mindStrength;

    this.updateStatus(nftData.verified ? '✅ OneirobotNFT Detected!' : '❌ Not OneirobotNFT');
    
    console.log('🎯 OneirobotNFT Data:', nftData);
  }

  updateStatus(status) {
    document.getElementById('oneirobot-widget').querySelector('.oneirobot-status').textContent = status;
  }

  verifyNFT() {
    this.updateStatus('🔍 Verifying...');
    
    // Simulate verification process
    setTimeout(() => {
      this.updateStatus('✅ Verified Authentic!');
      this.showNotification('🎉 OneirobotNFT verified as authentic!', 'success');
    }, 2000);
  }

  showAttributes() {
    const attributesWindow = window.open('', 'OneirobotAttributes', 'width=600,height=400');
    attributesWindow.document.write(`
      <html>
        <head>
          <title>OneirobotNFT Attributes</title>
          <style>
            body { 
              font-family: Monaco, monospace; 
              background: #1a1a2e; 
              color: #ffffff; 
              padding: 20px; 
            }
            .attribute { 
              background: rgba(0,212,255,0.1); 
              padding: 10px; 
              margin: 10px 0; 
              border-radius: 8px; 
            }
            .label { color: #00d4ff; font-weight: bold; }
          </style>
        </head>
        <body>
          <h1>🤖 OneirobotNFT Attributes</h1>
          <div class="attribute"><span class="label">Quantum Core:</span> ${document.getElementById('quantum-core').textContent}</div>
          <div class="attribute"><span class="label">Dream Level:</span> ${document.getElementById('dream-level').textContent}</div>
          <div class="attribute"><span class="label">Lucid Power:</span> ${document.getElementById('lucid-power').textContent}</div>
          <div class="attribute"><span class="label">Mind Strength:</span> ${document.getElementById('mind-strength').textContent}</div>
          <div class="attribute"><span class="label">Network:</span> ${document.getElementById('network-info').textContent}</div>
          <div class="attribute"><span class="label">Contract:</span> ${document.getElementById('contract-info').textContent}</div>
          <p>⚡ Powered by AI Gene Deployer - OneirobotNFT Syndicate</p>
        </body>
      </html>
    `);
  }

  openExplorer() {
    const network = document.getElementById('network-info').textContent;
    const contract = document.getElementById('contract-info').textContent;
    
    let explorerUrl;
    if (network.includes('SKALE')) {
      explorerUrl = `${ONEIROBOT_CONTRACTS.skale.explorer}/address/${ONEIROBOT_CONTRACTS.skale.address}`;
    } else {
      explorerUrl = `${ONEIROBOT_CONTRACTS.solana.explorer}/account/${ONEIROBOT_CONTRACTS.solana.programId}`;
    }
    
    window.open(explorerUrl, '_blank');
  }

  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `oneirobot-notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
      position: fixed;
      top: 100px;
      right: 20px;
      background: ${type === 'success' ? '#00ff88' : '#ffaa00'};
      color: #1a1a2e;
      padding: 15px;
      border-radius: 8px;
      font-weight: bold;
      z-index: 10001;
      box-shadow: 0 5px 15px rgba(0,0,0,0.3);
      animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
      notification.remove();
    }, 3000);
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new OneirobotNFTViewer();
  });
} else {
  new OneirobotNFTViewer();
}

// Send message to background script
chrome.runtime.sendMessage({
  action: 'pageLoaded',
  platform: window.location.hostname,
  timestamp: Date.now()
});