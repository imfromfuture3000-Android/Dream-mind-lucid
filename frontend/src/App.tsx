import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { WagmiProvider } from 'wagmi'
import { RainbowKitProvider, darkTheme } from '@rainbow-me/rainbowkit'
import { ConnectionProvider, WalletProvider } from '@solana/wallet-adapter-react'
import { WalletAdapterNetwork } from '@solana/wallet-adapter-base'
import { WalletModalProvider } from '@solana/wallet-adapter-react-ui'
import { clusterApiUrl } from '@solana/web3.js'
import { Toaster } from 'react-hot-toast'

// Import pages and components
import Navbar from '@/components/Navbar'
import HomePage from '@/components/pages/HomePage'
import DreamRecorder from '@/components/pages/DreamRecorder'
import Portfolio from '@/components/pages/Portfolio'
import Analytics from '@/components/pages/Analytics'
import Documentation from '@/components/pages/Documentation'
import ErrorBoundary from '@/components/ErrorBoundary'

// Import configurations
import { wagmiConfig } from '@/config/wagmi'
import { solanaWallets } from '@/config/solana'

// Import styles
import '@rainbow-me/rainbowkit/styles.css'
import '@solana/wallet-adapter-react-ui/styles.css'

// Create query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
    },
  },
})

// Solana network
const network = WalletAdapterNetwork.Mainnet
const endpoint = process.env.NODE_ENV === 'production' 
  ? process.env.VITE_SOLANA_RPC_URL || clusterApiUrl(network)
  : clusterApiUrl(WalletAdapterNetwork.Devnet)

function App() {
  return (
    <ErrorBoundary>
      <WagmiProvider config={wagmiConfig}>
        <QueryClientProvider client={queryClient}>
          <RainbowKitProvider 
            theme={darkTheme({
              accentColor: '#a855f7',
              accentColorForeground: 'white',
              borderRadius: 'medium',
            })}
          >
            <ConnectionProvider endpoint={endpoint}>
              <WalletProvider wallets={solanaWallets} autoConnect>
                <WalletModalProvider>
                  <Router>
                    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900">
                      <Navbar />
                      
                      <main className="container mx-auto px-4 py-8">
                        <Routes>
                          <Route path="/" element={<HomePage />} />
                          <Route path="/record" element={<DreamRecorder />} />
                          <Route path="/portfolio" element={<Portfolio />} />
                          <Route path="/analytics" element={<Analytics />} />
                          <Route path="/docs" element={<Documentation />} />
                        </Routes>
                      </main>
                      
                      {/* Toast notifications */}
                      <Toaster 
                        position="bottom-right"
                        toastOptions={{
                          duration: 4000,
                          style: {
                            background: 'rgba(0, 0, 0, 0.8)',
                            color: '#fff',
                            backdropFilter: 'blur(8px)',
                          },
                        }}
                      />
                    </div>
                  </Router>
                </WalletModalProvider>
              </WalletProvider>
            </ConnectionProvider>
          </RainbowKitProvider>
        </QueryClientProvider>
      </WagmiProvider>
    </ErrorBoundary>
  )
}

export default App