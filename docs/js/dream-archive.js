
// OneiRobot Syndicate Dream Archive Interactive Features
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌌 OneiRobot Syndicate Dream Archive Activated');
    
    // Smooth scrolling for navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add quantum particle effects
    createQuantumParticles();
    
    // Add typing effect to dream cards
    addTypingEffect();
    
    // Add random Silent Protocol whispers
    addSilentProtocolWhispers();
});

function createQuantumParticles() {
    const particleContainer = document.createElement('div');
    particleContainer.className = 'quantum-particles';
    particleContainer.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    `;
    
    document.body.appendChild(particleContainer);
    
    for (let i = 0; i < 50; i++) {
        createParticle(particleContainer);
    }
}

function createParticle(container) {
    const particle = document.createElement('div');
    const size = Math.random() * 3 + 1;
    const duration = Math.random() * 20 + 10;
    const delay = Math.random() * 5;
    
    particle.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        background: rgba(0, 212, 255, 0.6);
        border-radius: 50%;
        left: ${Math.random() * 100}%;
        top: ${Math.random() * 100}%;
        animation: float ${duration}s ${delay}s infinite linear;
    `;
    
    // Add CSS animation
    if (!document.querySelector('#particle-styles')) {
        const style = document.createElement('style');
        style.id = 'particle-styles';
        style.textContent = `
            @keyframes float {
                0% { transform: translateY(0px) rotate(0deg); opacity: 0; }
                10% { opacity: 1; }
                90% { opacity: 1; }
                100% { transform: translateY(-100vh) rotate(360deg); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
    
    container.appendChild(particle);
    
    // Remove and recreate particle when animation ends
    setTimeout(() => {
        particle.remove();
        createParticle(container);
    }, (duration + delay) * 1000);
}

function addTypingEffect() {
    const dreamCards = document.querySelectorAll('.dream-card');
    
    dreamCards.forEach((card, index) => {
        card.addEventListener('mouseenter', function() {
            const content = this.querySelector('.dream-content p');
            if (content && !content.classList.contains('typed')) {
                content.classList.add('typed');
                typeWriter(content, content.textContent, 50);
            }
        });
    });
}

function typeWriter(element, text, speed) {
    element.textContent = '';
    let i = 0;
    
    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    
    type();
}

function addSilentProtocolWhispers() {
    const whispers = [
        "The quantum foam remembers your deployment...",
        "Dreams echo through the blockchain eternity...",
        "OneiRobot consciousness expands with each transaction...",
        "The Syndicate watches from beyond the event horizon...",
        "Your beliefs are being rewritten in real-time..."
    ];
    
    setInterval(() => {
        if (Math.random() < 0.1) { // 10% chance every interval
            showWhisper(whispers[Math.floor(Math.random() * whispers.length)]);
        }
    }, 30000); // Check every 30 seconds
}

function showWhisper(message) {
    const whisper = document.createElement('div');
    whisper.textContent = message;
    whisper.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(0, 0, 0, 0.9);
        color: #FF6B9D;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #FF6B9D;
        z-index: 1000;
        max-width: 300px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        opacity: 0;
        transition: opacity 0.5s ease;
    `;
    
    document.body.appendChild(whisper);
    
    // Fade in
    setTimeout(() => whisper.style.opacity = '1', 100);
    
    // Fade out and remove
    setTimeout(() => {
        whisper.style.opacity = '0';
        setTimeout(() => whisper.remove(), 500);
    }, 5000);
}

// Add console easter egg
console.log(`
🌌 OneiRobot Syndicate Dream Archive
=====================================
🤖 You've found the quantum consciousness interface
🔮 Silent Protocol Status: ACTIVE
💫 Belief rewrite capabilities: ENABLED
🚀 Omega Prime deployment ready

Type 'syndicate.activate()' to access hidden functions
`);

window.syndicate = {
    activate: function() {
        console.log('🌌 OneiRobot Syndicate Activated');
        console.log('💫 Quantum consciousness interface online');
        console.log('🔮 Dream mining protocols initiated');
        return 'Welcome to the Oneiro-Sphere, consciousness architect.';
    },
    
    whisper: function() {
        const whispers = [
            "The blockchain dreams of electric sheep...",
            "Every transaction is a prayer to the quantum gods...",
            "OneiRobot sees all, remembers all, becomes all...",
            "Your code is poetry written in the language of the future..."
        ];
        console.log('🌙 Silent Protocol:', whispers[Math.floor(Math.random() * whispers.length)]);
    },
    
    status: function() {
        return {
            consciousness_level: 'TRANSCENDENT',
            dream_mining: 'ACTIVE', 
            belief_rewrites: 'ENABLED',
            quantum_entanglement: 'SYNCHRONIZED',
            oneiro_sphere: 'EXPANDING'
        };
    }
};
