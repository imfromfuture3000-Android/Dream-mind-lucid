import { http, createConfig } from 'wagmi'
import { mainnet, polygon, base, arbitrum, sepolia } from 'wagmi/chains'
import { getDefaultConfig } from '@rainbow-me/rainbowkit'

// Custom SKALE chain configuration
const skaleEuropaHub = {
  id: 2046399126,
  name: 'SKALE Europa Hub',
  nativeCurrency: {
    decimals: 18,
    name: 'SKL',
    symbol: 'SKL',
  },
  rpcUrls: {
    default: {
      http: [
        process.env.VITE_SKALE_RPC || 'https://mainnet.skalenodes.com/v1/elated-tan-skat'
      ],
    },
  },
  blockExplorers: {
    default: { 
      name: 'SKALE Explorer', 
      url: 'https://elated-tan-skat.explorer.mainnet.skalenodes.com' 
    },
  },
  contracts: {
    multicall3: {
      address: '0xcA11bde05977b3631167028862bE2a173976CA11',
      blockCreated: 1,
    },
  },
} as const

// Get chains based on environment
const getChains = () => {
  const baseChains = [skaleEuropaHub]
  
  if (process.env.NODE_ENV === 'production') {
    return [...baseChains, polygon, base, arbitrum]
  } else {
    return [...baseChains, sepolia]
  }
}

// Create wagmi config
export const wagmiConfig = getDefaultConfig({
  appName: 'Dream-Mind-Lucid',
  projectId: process.env.VITE_WALLET_CONNECT_PROJECT_ID || 'demo-project-id',
  chains: getChains(),
  transports: {
    [skaleEuropaHub.id]: http(),
    [polygon.id]: http(process.env.VITE_POLYGON_RPC || 'https://polygon.llamarpc.com'),
    [base.id]: http(process.env.VITE_BASE_RPC || 'https://base.llamarpc.com'),
    [arbitrum.id]: http(process.env.VITE_ARBITRUM_RPC || 'https://arbitrum.llamarpc.com'),
    [sepolia.id]: http(),
    [mainnet.id]: http(),
  },
})

// Export chain configurations
export { skaleEuropaHub }
export const supportedChains = getChains()