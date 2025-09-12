// Contract addresses for different networks
export const contractAddresses = {
  skale: {
    IEMDreams: process.env.VITE_SKALE_DREAMS_ADDRESS || '',
    OneiroSphere: process.env.VITE_SKALE_ONEIRO_ADDRESS || '',
    DreamStaking: process.env.VITE_SKALE_STAKING_ADDRESS || '',
  },
  polygon: {
    IEMDreams: process.env.VITE_POLYGON_DREAMS_ADDRESS || '',
    OneiroSphere: process.env.VITE_POLYGON_ONEIRO_ADDRESS || '',
    DreamStaking: process.env.VITE_POLYGON_STAKING_ADDRESS || '',
  },
  base: {
    IEMDreams: process.env.VITE_BASE_DREAMS_ADDRESS || '',
    OneiroSphere: process.env.VITE_BASE_ONEIRO_ADDRESS || '',
    DreamStaking: process.env.VITE_BASE_STAKING_ADDRESS || '',
  },
  arbitrum: {
    IEMDreams: process.env.VITE_ARBITRUM_DREAMS_ADDRESS || '',
    OneiroSphere: process.env.VITE_ARBITRUM_ONEIRO_ADDRESS || '',
    DreamStaking: process.env.VITE_ARBITRUM_STAKING_ADDRESS || '',
  },
  solana: {
    treasury: process.env.VITE_SOLANA_TREASURY_ADDRESS || '4eJZVbbsiLAG6EkWvgEYEWKEpdhJPFBYMeJ6DBX98w6a',
    dreamMint: process.env.VITE_SOLANA_DREAM_MINT || '',
    smindMint: process.env.VITE_SOLANA_SMIND_MINT || '',
    lucidMint: process.env.VITE_SOLANA_LUCID_MINT || '',
  },
} as const

// Relayer configurations
export const relayerConfig = {
  biconomy: {
    apiKey: process.env.VITE_BICONOMY_API_KEY || '',
    bundlerUrl: 'https://bundler.biconomy.io/api/v2',
    paymasterUrl: 'https://paymaster.biconomy.io/api/v1',
  },
  gelato: {
    apiKey: process.env.VITE_GELATO_API_KEY || '',
    relayUrl: 'https://relay.gelato.digital',
  },
} as const

// IPFS configuration
export const ipfsConfig = {
  gateway: process.env.VITE_IPFS_GATEWAY || 'https://gateway.pinata.cloud/ipfs/',
  apiUrl: process.env.VITE_IPFS_API_URL || 'https://api.pinata.cloud',
  apiKey: process.env.VITE_PINATA_API_KEY || '',
  secretKey: process.env.VITE_PINATA_SECRET_KEY || '',
} as const

// App configuration
export const appConfig = {
  name: 'Dream-Mind-Lucid',
  description: 'Zero-Cost Multi-Chain Dream Ecosystem',
  url: process.env.VITE_APP_URL || 'https://dream-mind-lucid.vercel.app',
  version: '1.0.0',
  social: {
    github: 'https://github.com/imfromfuture3000-Android/Dream-mind-lucid',
    twitter: 'https://twitter.com/DreamMindLucid',
    discord: 'https://discord.gg/DreamMindLucid',
  },
} as const

// Feature flags
export const features = {
  gaslessTransactions: true,
  ipfsStorage: true,
  multiChain: true,
  stakingRewards: true,
  analytics: true,
  socialFeatures: false, // Coming soon
} as const

// Network-specific gas configurations
export const gasConfig = {
  skale: {
    gasPrice: 0, // Zero gas on SKALE
    gasLimit: 8000000,
  },
  polygon: {
    gasPrice: 'auto',
    gasLimit: 2000000,
    maxFeePerGas: 100000000000, // 100 gwei
    maxPriorityFeePerGas: 2000000000, // 2 gwei
  },
  base: {
    gasPrice: 'auto',
    gasLimit: 2000000,
  },
  arbitrum: {
    gasPrice: 'auto',
    gasLimit: 2000000,
  },
} as const