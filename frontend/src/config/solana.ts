import {
  PhantomWalletAdapter,
  SolflareWalletAdapter,
  TorusWalletAdapter,
  BackpackWalletAdapter,
} from '@solana/wallet-adapter-wallets'

// Configure Solana wallets
export const solanaWallets = [
  new PhantomWalletAdapter(),
  new SolflareWalletAdapter(),
  new BackpackWalletAdapter(),
  new TorusWalletAdapter(),
]

// Solana cluster configuration
export const solanaConfig = {
  mainnet: {
    endpoint: process.env.VITE_SOLANA_RPC_URL || 'https://mainnet.helius-rpc.com',
    commitment: 'confirmed' as const,
  },
  devnet: {
    endpoint: 'https://api.devnet.solana.com',
    commitment: 'confirmed' as const,
  },
  testnet: {
    endpoint: 'https://api.testnet.solana.com',
    commitment: 'confirmed' as const,
  },
} as const

export const currentSolanaConfig = process.env.NODE_ENV === 'production' 
  ? solanaConfig.mainnet 
  : solanaConfig.devnet