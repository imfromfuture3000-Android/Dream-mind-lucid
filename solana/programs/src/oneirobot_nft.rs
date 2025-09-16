use anchor_lang::prelude::*;
use anchor_spl::{
    associated_token::AssociatedToken,
    metadata::{
        create_master_edition_v3, create_metadata_accounts_v3, CreateMasterEditionV3,
        CreateMetadataAccountsV3, Metadata,
    },
    token::{mint_to, Mint, MintTo, Token, TokenAccount},
};
use mpl_token_metadata::{
    pda::{find_master_edition_account, find_metadata_account},
    state::{DataV2, Creator},
};

declare_id!("Oneir8BotPr0gram1DSynt1cat3M4st3r5");

/**
 * OneirobotNFT Solana Program - Metaplex Integration
 * AI Gene Deployer - Rust/Anchor Implementation
 * Features: PDA-based allowlist, Quantum Core attributes, IPFS metadata
 */

#[program]
pub mod oneirobot_nft {
    use super::*;

    /// Initialize the OneirobotNFT program
    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        let oneirobot_state = &mut ctx.accounts.oneirobot_state;
        oneirobot_state.authority = ctx.accounts.authority.key();
        oneirobot_state.total_minted = 0;
        oneirobot_state.max_supply = 10_000;
        oneirobot_state.mint_price = 0; // Zero cost on Solana
        oneirobot_state.is_minting_enabled = true;
        
        // Initialize syndicate masters
        oneirobot_state.syndicate_masters = vec![
            ctx.accounts.authority.key(),
            // Add more syndicate masters here
        ];

        msg!("OneirobotNFT program initialized with authority: {}", oneirobot_state.authority);
        Ok(())
    }

    /// Add a syndicate master to the allowlist
    pub fn add_syndicate_master(
        ctx: Context<AddSyndicateMaster>,
        new_master: Pubkey,
    ) -> Result<()> {
        let oneirobot_state = &mut ctx.accounts.oneirobot_state;
        
        require!(
            ctx.accounts.authority.key() == oneirobot_state.authority,
            OneirobotError::UnauthorizedAccess
        );

        if !oneirobot_state.syndicate_masters.contains(&new_master) {
            oneirobot_state.syndicate_masters.push(new_master);
            msg!("Added syndicate master: {}", new_master);
        }

        Ok(())
    }

    /// Mint OneirobotNFT - Restricted to Syndicate Masters
    pub fn mint_oneirobot(
        ctx: Context<MintOneirobot>,
        metadata_uri: String,
        name: String,
        symbol: String,
    ) -> Result<()> {
        let oneirobot_state = &mut ctx.accounts.oneirobot_state;
        
        // Check if minter is syndicate master
        require!(
            oneirobot_state.syndicate_masters.contains(&ctx.accounts.minter.key()),
            OneirobotError::NotSyndicateMaster
        );

        // Check supply limit
        require!(
            oneirobot_state.total_minted < oneirobot_state.max_supply,
            OneirobotError::MaxSupplyReached
        );

        require!(
            oneirobot_state.is_minting_enabled,
            OneirobotError::MintingDisabled
        );

        // Generate pseudorandom attributes
        let clock = Clock::get()?;
        let random_seed = generate_pseudo_random_seed(
            &ctx.accounts.mint.key(),
            &ctx.accounts.recipient.key(),
            clock.slot,
            clock.unix_timestamp,
        );

        let attributes = generate_oneirobot_attributes(random_seed, &metadata_uri);

        // Mint NFT token
        let cpi_accounts = MintTo {
            mint: ctx.accounts.mint.to_account_info(),
            to: ctx.accounts.token_account.to_account_info(),
            authority: ctx.accounts.mint_authority.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts);
        mint_to(cpi_ctx, 1)?;

        // Create metadata account
        let creator = vec![Creator {
            address: oneirobot_state.authority,
            verified: false,
            share: 100,
        }];

        let data_v2 = DataV2 {
            name: name.clone(),
            symbol: symbol.clone(),
            uri: metadata_uri.clone(),
            seller_fee_basis_points: 500, // 5% royalty
            creators: Some(creator),
            collection: None,
            uses: None,
        };

        let metadata_ctx = CpiContext::new(
            ctx.accounts.metadata_program.to_account_info(),
            CreateMetadataAccountsV3 {
                metadata: ctx.accounts.metadata.to_account_info(),
                mint: ctx.accounts.mint.to_account_info(),
                mint_authority: ctx.accounts.mint_authority.to_account_info(),
                update_authority: ctx.accounts.mint_authority.to_account_info(),
                payer: ctx.accounts.minter.to_account_info(),
                system_program: ctx.accounts.system_program.to_account_info(),
                rent: ctx.accounts.rent.to_account_info(),
            },
        );

        create_metadata_accounts_v3(metadata_ctx, data_v2, true, true, None)?;

        // Create master edition
        let master_edition_ctx = CpiContext::new(
            ctx.accounts.metadata_program.to_account_info(),
            CreateMasterEditionV3 {
                edition: ctx.accounts.master_edition.to_account_info(),
                mint: ctx.accounts.mint.to_account_info(),
                update_authority: ctx.accounts.mint_authority.to_account_info(),
                mint_authority: ctx.accounts.mint_authority.to_account_info(),
                payer: ctx.accounts.minter.to_account_info(),
                metadata: ctx.accounts.metadata.to_account_info(),
                token_program: ctx.accounts.token_program.to_account_info(),
                system_program: ctx.accounts.system_program.to_account_info(),
                rent: ctx.accounts.rent.to_account_info(),
            },
        );

        create_master_edition_v3(master_edition_ctx, Some(0))?;

        // Store NFT attributes
        let nft_attributes = &mut ctx.accounts.nft_attributes;
        nft_attributes.mint = ctx.accounts.mint.key();
        nft_attributes.owner = ctx.accounts.recipient.key();
        nft_attributes.quantum_core = attributes.quantum_core;
        nft_attributes.dream_level = attributes.dream_level;
        nft_attributes.lucid_power = attributes.lucid_power;
        nft_attributes.mind_strength = attributes.mind_strength;
        nft_attributes.metadata_uri = metadata_uri;
        nft_attributes.mint_timestamp = clock.unix_timestamp;
        nft_attributes.random_seed = random_seed;
        nft_attributes.token_id = oneirobot_state.total_minted;

        // Update state
        oneirobot_state.total_minted += 1;

        emit!(OneirobotMintedEvent {
            mint: ctx.accounts.mint.key(),
            owner: ctx.accounts.recipient.key(),
            token_id: nft_attributes.token_id,
            quantum_core: attributes.quantum_core.clone(),
            dream_level: attributes.dream_level,
            lucid_power: attributes.lucid_power,
            mind_strength: attributes.mind_strength,
            metadata_uri: metadata_uri,
            timestamp: clock.unix_timestamp,
        });

        msg!(
            "OneirobotNFT minted! Token ID: {}, Quantum Core: {}",
            nft_attributes.token_id,
            attributes.quantum_core
        );

        Ok(())
    }

    /// Get NFT attributes by mint address
    pub fn get_nft_attributes(ctx: Context<GetNftAttributes>) -> Result<NftAttributes> {
        let nft_attributes = &ctx.accounts.nft_attributes;
        Ok(nft_attributes.clone())
    }
}

// ===================== ACCOUNTS =====================

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + OneirobotState::SPACE,
        seeds = [b"oneirobot_state"],
        bump
    )]
    pub oneirobot_state: Account<'info, OneirobotState>,
    
    #[account(mut)]
    pub authority: Signer<'info>,
    
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct AddSyndicateMaster<'info> {
    #[account(
        mut,
        seeds = [b"oneirobot_state"],
        bump
    )]
    pub oneirobot_state: Account<'info, OneirobotState>,
    
    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct MintOneirobot<'info> {
    #[account(
        mut,
        seeds = [b"oneirobot_state"],
        bump
    )]
    pub oneirobot_state: Account<'info, OneirobotState>,

    #[account(
        init,
        payer = minter,
        space = 8 + NftAttributes::SPACE,
        seeds = [b"nft_attributes", mint.key().as_ref()],
        bump
    )]
    pub nft_attributes: Account<'info, NftAttributes>,

    #[account(
        init,
        payer = minter,
        mint::decimals = 0,
        mint::authority = mint_authority,
    )]
    pub mint: Account<'info, Mint>,

    #[account(
        init,
        payer = minter,
        associated_token::mint = mint,
        associated_token::authority = recipient,
    )]
    pub token_account: Account<'info, TokenAccount>,

    /// CHECK: Metadata account
    #[account(
        mut,
        seeds = [
            b"metadata",
            metadata_program.key().as_ref(),
            mint.key().as_ref(),
        ],
        seeds::program = metadata_program.key(),
        bump
    )]
    pub metadata: UncheckedAccount<'info>,

    /// CHECK: Master edition account
    #[account(
        mut,
        seeds = [
            b"metadata",
            metadata_program.key().as_ref(),
            mint.key().as_ref(),
            b"edition",
        ],
        seeds::program = metadata_program.key(),
        bump
    )]
    pub master_edition: UncheckedAccount<'info>,

    #[account(mut)]
    pub minter: Signer<'info>,

    /// CHECK: Recipient of the NFT
    pub recipient: AccountInfo<'info>,

    /// CHECK: Mint authority (could be a PDA)
    pub mint_authority: AccountInfo<'info>,

    pub rent: Sysvar<'info, Rent>,
    pub system_program: Program<'info, System>,
    pub token_program: Program<'info, Token>,
    pub associated_token_program: Program<'info, AssociatedToken>,
    
    /// CHECK: Metaplex metadata program
    pub metadata_program: AccountInfo<'info>,
}

#[derive(Accounts)]
pub struct GetNftAttributes<'info> {
    #[account(
        seeds = [b"nft_attributes", mint.key().as_ref()],
        bump
    )]
    pub nft_attributes: Account<'info, NftAttributes>,
    
    pub mint: Account<'info, Mint>,
}

// ===================== STATE STRUCTURES =====================

#[account]
pub struct OneirobotState {
    pub authority: Pubkey,
    pub total_minted: u64,
    pub max_supply: u64,
    pub mint_price: u64,
    pub is_minting_enabled: bool,
    pub syndicate_masters: Vec<Pubkey>,
}

impl OneirobotState {
    pub const SPACE: usize = 32 + 8 + 8 + 8 + 1 + (4 + 32 * 10); // Max 10 syndicate masters
}

#[account]
#[derive(Clone)]
pub struct NftAttributes {
    pub mint: Pubkey,
    pub owner: Pubkey,
    pub token_id: u64,
    pub quantum_core: String,
    pub dream_level: u8,
    pub lucid_power: u8,
    pub mind_strength: u8,
    pub metadata_uri: String,
    pub mint_timestamp: i64,
    pub random_seed: u64,
}

impl NftAttributes {
    pub const SPACE: usize = 32 + 32 + 8 + (4 + 32) + 1 + 1 + 1 + (4 + 200) + 8 + 8; // Approx sizes
}

#[derive(Clone)]
pub struct GeneratedAttributes {
    pub quantum_core: String,
    pub dream_level: u8,
    pub lucid_power: u8,
    pub mind_strength: u8,
}

// ===================== EVENTS =====================

#[event]
pub struct OneirobotMintedEvent {
    pub mint: Pubkey,
    pub owner: Pubkey,
    pub token_id: u64,
    pub quantum_core: String,
    pub dream_level: u8,
    pub lucid_power: u8,
    pub mind_strength: u8,
    pub metadata_uri: String,
    pub timestamp: i64,
}

// ===================== ERRORS =====================

#[error_code]
pub enum OneirobotError {
    #[msg("Unauthorized access - not the program authority")]
    UnauthorizedAccess,
    #[msg("Not a syndicate master - minting restricted")]
    NotSyndicateMaster,
    #[msg("Maximum supply reached")]
    MaxSupplyReached,
    #[msg("Minting is currently disabled")]
    MintingDisabled,
    #[msg("Invalid metadata URI")]
    InvalidMetadataUri,
    #[msg("NFT attributes not found")]
    AttributesNotFound,
}

// ===================== HELPER FUNCTIONS =====================

/// Generate pseudorandom seed using available blockchain data
/// WARNING: For mainnet, consider using Helius RNG or Switchboard VRF for true randomness
pub fn generate_pseudo_random_seed(
    mint: &Pubkey,
    recipient: &Pubkey,
    slot: u64,
    timestamp: i64,
) -> u64 {
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};

    let mut hasher = DefaultHasher::new();
    mint.hash(&mut hasher);
    recipient.hash(&mut hasher);
    slot.hash(&mut hasher);
    timestamp.hash(&mut hasher);
    
    hasher.finish()
}

/// Generate OneirobotNFT attributes from random seed
pub fn generate_oneirobot_attributes(random_seed: u64, metadata_uri: &str) -> GeneratedAttributes {
    let quantum_cores = [
        "Quantum Core Alpha",
        "Quantum Core Beta", 
        "Quantum Core Gamma",
        "Quantum Core Delta",
        "Quantum Core Epsilon",
        "Quantum Core Zeta",
        "Quantum Core Omega",
    ];

    let quantum_core = quantum_cores[(random_seed % quantum_cores.len() as u64) as usize].to_string();
    let dream_level = ((random_seed >> 8) % 100) as u8 + 1;  // 1-100
    let lucid_power = ((random_seed >> 16) % 100) as u8 + 1; // 1-100
    let mind_strength = ((random_seed >> 24) % 100) as u8 + 1; // 1-100

    GeneratedAttributes {
        quantum_core,
        dream_level,
        lucid_power,
        mind_strength,
    }
}