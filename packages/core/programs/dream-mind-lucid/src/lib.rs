use anchor_lang::prelude::*;
use anchor_spl::token_2022::{self, Token2022, TokenAccount, Mint};
use anchor_spl::associated_token::AssociatedToken;

declare_id!("5oDxEKGa78LjcE9zMFqz1vLLgKYj4Drd6k1Vq2GJ6YNm");

// Token supply constants (from project spec)
const DREAM_TOTAL_SUPPLY: u64 = 777_777_777 * 1_000_000_000; // 777,777,777 DREAM with 9 decimals
const SMIND_TOTAL_SUPPLY: u64 = 777_777_777 * 1_000_000_000; // 777,777,777 SMIND with 9 decimals  
const LUCID_TOTAL_SUPPLY: u64 = 333_333_333 * 1_000_000_000; // 333,333,333 LUCID with 9 decimals

const DREAM_REWARD_PER_RECORD: u64 = 10 * 1_000_000_000; // 10 DREAM tokens per dream record

#[program]
pub mod dream_mind_lucid {
    use super::*;

    pub fn initialize_tokens(ctx: Context<InitializeTokens>) -> Result<()> {
        msg!("Initializing Dream-Mind-Lucid token ecosystem");
        
        // Initialize treasury account for managing token distributions
        let treasury = &mut ctx.accounts.treasury;
        treasury.authority = ctx.accounts.authority.key();
        treasury.dream_mint = ctx.accounts.dream_mint.key();
        treasury.smind_mint = ctx.accounts.smind_mint.key();
        treasury.lucid_mint = ctx.accounts.lucid_mint.key();
        treasury.total_dreams_recorded = 0;
        treasury.total_rewards_distributed = 0;
        treasury.mev_protection_enabled = true;
        
        msg!("Token ecosystem initialized with treasury: {}", treasury.authority);
        Ok(())
    }

    pub fn record_dream(ctx: Context<RecordDream>, dream_content_hash: [u8; 32]) -> Result<()> {
        let treasury = &mut ctx.accounts.treasury;
        let dream_record = &mut ctx.accounts.dream_record;
        let clock = Clock::get()?;
        
        // Record dream metadata
        dream_record.dreamer = ctx.accounts.dreamer.key();
        dream_record.content_hash = dream_content_hash;
        dream_record.timestamp = clock.unix_timestamp;
        dream_record.token_reward = DREAM_REWARD_PER_RECORD;
        dream_record.mev_protected = treasury.mev_protection_enabled;
        dream_record.id = treasury.total_dreams_recorded;
        
        // Update treasury stats
        treasury.total_dreams_recorded += 1;
        treasury.total_rewards_distributed += DREAM_REWARD_PER_RECORD;
        
        // Mint DREAM tokens as reward (implementation via CPI to token program)
        let cpi_accounts = token_2022::MintTo {
            mint: ctx.accounts.dream_mint.to_account_info(),
            to: ctx.accounts.dreamer_dream_account.to_account_info(),
            authority: ctx.accounts.treasury.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts);
        
        token_2022::mint_to(cpi_ctx, DREAM_REWARD_PER_RECORD)?;
        
        msg!("Dream recorded! ID: {}, Reward: {} DREAM", dream_record.id, DREAM_REWARD_PER_RECORD / 1_000_000_000);
        Ok(())
    }

    pub fn interface_dream(ctx: Context<InterfaceDream>, ipfs_hash: String) -> Result<()> {
        let dream_interface = &mut ctx.accounts.dream_interface;
        let clock = Clock::get()?;
        
        dream_interface.dreamer = ctx.accounts.dreamer.key();
        dream_interface.ipfs_hash = ipfs_hash;
        dream_interface.timestamp = clock.unix_timestamp;
        dream_interface.access_level = 1; // Basic access
        
        msg!("Dream interfaced via IPFS: {}", dream_interface.ipfs_hash);
        Ok(())
    }

    pub fn stake_for_lucid_access(ctx: Context<StakeLucid>, amount: u64) -> Result<()> {
        let stake_account = &mut ctx.accounts.stake_account;
        let clock = Clock::get()?;
        
        // Transfer LUCID tokens to stake account
        let cpi_accounts = token_2022::Transfer {
            from: ctx.accounts.user_lucid_account.to_account_info(),
            to: ctx.accounts.lucid_stake_vault.to_account_info(),
            authority: ctx.accounts.user.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts);
        
        token_2022::transfer(cpi_ctx, amount)?;
        
        stake_account.user = ctx.accounts.user.key();
        stake_account.amount = amount;
        stake_account.timestamp = clock.unix_timestamp;
        stake_account.access_level = calculate_access_level(amount);
        
        msg!("LUCID tokens staked: {}, Access level: {}", amount, stake_account.access_level);
        Ok(())
    }
}

fn calculate_access_level(amount: u64) -> u8 {
    // Calculate access level based on LUCID stake amount
    match amount {
        0..=1_000_000_000 => 1,           // 0-1 LUCID: Basic
        1_000_000_001..=10_000_000_000 => 2,  // 1-10 LUCID: Premium  
        10_000_000_001..=100_000_000_000 => 3, // 10-100 LUCID: VIP
        _ => 4,                                  // 100+ LUCID: Quantum
    }
}

#[derive(Accounts)]
pub struct InitializeTokens<'info> {
    #[account(mut)]
    pub authority: Signer<'info>,
    
    #[account(
        init,
        payer = authority,
        space = 8 + std::mem::size_of::<Treasury>(),
        seeds = [b"treasury"],
        bump
    )]
    pub treasury: Account<'info, Treasury>,
    
    pub dream_mint: Account<'info, Mint>,
    pub smind_mint: Account<'info, Mint>,
    pub lucid_mint: Account<'info, Mint>,
    
    pub system_program: Program<'info, System>,
    pub token_program: Program<'info, Token2022>,
}

#[derive(Accounts)]
pub struct RecordDream<'info> {
    #[account(mut)]
    pub dreamer: Signer<'info>,
    
    #[account(
        mut,
        seeds = [b"treasury"],
        bump
    )]
    pub treasury: Account<'info, Treasury>,
    
    #[account(
        init,
        payer = dreamer,
        space = 8 + std::mem::size_of::<DreamRecord>(),
        seeds = [b"dream", dreamer.key().as_ref(), &treasury.total_dreams_recorded.to_le_bytes()],
        bump
    )]
    pub dream_record: Account<'info, DreamRecord>,
    
    #[account(mut)]
    pub dream_mint: Account<'info, Mint>,
    
    #[account(
        mut,
        associated_token::mint = dream_mint,
        associated_token::authority = dreamer,
        associated_token::token_program = token_program
    )]
    pub dreamer_dream_account: Account<'info, TokenAccount>,
    
    pub system_program: Program<'info, System>,
    pub token_program: Program<'info, Token2022>,
    pub associated_token_program: Program<'info, AssociatedToken>,
}

#[derive(Accounts)]
pub struct InterfaceDream<'info> {
    #[account(mut)]
    pub dreamer: Signer<'info>,
    
    #[account(
        init,
        payer = dreamer,
        space = 8 + std::mem::size_of::<DreamInterface>(),
        seeds = [b"interface", dreamer.key().as_ref()],
        bump
    )]
    pub dream_interface: Account<'info, DreamInterface>,
    
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct StakeLucid<'info> {
    #[account(mut)]
    pub user: Signer<'info>,
    
    #[account(
        init,
        payer = user,
        space = 8 + std::mem::size_of::<LucidStake>(),
        seeds = [b"stake", user.key().as_ref()],
        bump
    )]
    pub stake_account: Account<'info, LucidStake>,
    
    #[account(mut)]
    pub user_lucid_account: Account<'info, TokenAccount>,
    
    #[account(mut)]
    pub lucid_stake_vault: Account<'info, TokenAccount>,
    
    pub token_program: Program<'info, Token2022>,
    pub system_program: Program<'info, System>,
}

#[account]
pub struct Treasury {
    pub authority: Pubkey,
    pub dream_mint: Pubkey,
    pub smind_mint: Pubkey,
    pub lucid_mint: Pubkey,
    pub total_dreams_recorded: u64,
    pub total_rewards_distributed: u64,
    pub mev_protection_enabled: bool,
}

#[account]
pub struct DreamRecord {
    pub id: u64,
    pub dreamer: Pubkey,
    pub content_hash: [u8; 32],
    pub timestamp: i64,
    pub token_reward: u64,
    pub mev_protected: bool,
}

#[account]
pub struct DreamInterface {
    pub dreamer: Pubkey,
    pub ipfs_hash: String,
    pub timestamp: i64,
    pub access_level: u8,
}

#[account]
pub struct LucidStake {
    pub user: Pubkey,
    pub amount: u64,
    pub timestamp: i64,
    pub access_level: u8,
}

#[error_code]
pub enum DreamError {
    #[msg("Insufficient LUCID tokens for access")]
    InsufficientLucidAccess,
    #[msg("Dream content too large")]
    DreamContentTooLarge,
    #[msg("MEV protection failed")]
    MevProtectionFailed,
    #[msg("Invalid access level")]
    InvalidAccessLevel,
}