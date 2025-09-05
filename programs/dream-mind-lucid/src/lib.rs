use anchor_lang::prelude::*;
use anchor_spl::{
    associated_token::AssociatedToken,
    token_2022::{Token2022, TokenAccount, Mint},
    token_interface::{Mint as MintInterface, TokenAccount as TokenAccountInterface},
};

declare_id!("4eJZVbbsiLAG6EkWvgEYEWKEpdhJPFBYMeJ6DBX98w6a");

#[program]
pub mod dream_mind_lucid {
    use super::*;

    /// Initialize the dream ecosystem with SPL Token 2022 mints
    pub fn initialize(
        ctx: Context<Initialize>,
        treasury_bump: u8,
    ) -> Result<()> {
        let treasury = &mut ctx.accounts.treasury;
        treasury.bump = treasury_bump;
        treasury.authority = ctx.accounts.authority.key();
        treasury.dream_mint = ctx.accounts.dream_mint.key();
        treasury.smind_mint = ctx.accounts.smind_mint.key();
        treasury.lucid_mint = ctx.accounts.lucid_mint.key();
        treasury.total_dreams = 0;
        treasury.total_sol_rebates = 0;
        
        emit!(TreasuryInitialized {
            authority: treasury.authority,
            dream_mint: treasury.dream_mint,
            smind_mint: treasury.smind_mint,
            lucid_mint: treasury.lucid_mint,
        });

        Ok(())
    }

    /// Record a dream on the Solana blockchain with IPFS hash
    pub fn record_dream(
        ctx: Context<RecordDream>,
        ipfs_hash: String,
        dream_content: String,
    ) -> Result<()> {
        require!(ipfs_hash.len() > 0, ErrorCode::EmptyIpfsHash);
        require!(dream_content.len() <= 1000, ErrorCode::DreamTooLong);

        let dream_record = &mut ctx.accounts.dream_record;
        let treasury = &mut ctx.accounts.treasury;
        
        dream_record.dreamer = ctx.accounts.dreamer.key();
        dream_record.ipfs_hash = ipfs_hash.clone();
        dream_record.dream_content = dream_content.clone();
        dream_record.timestamp = Clock::get()?.unix_timestamp;
        dream_record.validated = false;
        dream_record.reward_claimed = false;

        treasury.total_dreams += 1;

        // Emit dream recorded event
        emit!(DreamRecorded {
            dreamer: dream_record.dreamer,
            ipfs_hash: ipfs_hash,
            dream_content: dream_content,
            timestamp: dream_record.timestamp,
        });

        Ok(())
    }

    /// Validate dream and mint DREAM tokens as reward
    pub fn validate_dream(
        ctx: Context<ValidateDream>,
        validation_score: u8,
    ) -> Result<()> {
        require!(validation_score <= 100, ErrorCode::InvalidValidationScore);
        
        let dream_record = &mut ctx.accounts.dream_record;
        require!(!dream_record.validated, ErrorCode::AlreadyValidated);
        
        dream_record.validated = true;
        dream_record.validation_score = validation_score;

        // Calculate reward based on validation score (10-1000 DREAM tokens)
        let base_reward = 10_000_000; // 10 DREAM tokens (6 decimals)
        let score_multiplier = validation_score as u64;
        let reward_amount = base_reward + (score_multiplier * 1_000_000); // Up to 100 additional DREAM

        // Mint DREAM tokens to dreamer
        let treasury_seeds = &[
            b"treasury",
            &[ctx.accounts.treasury.bump],
        ];
        let signer = &[&treasury_seeds[..]];

        let cpi_accounts = anchor_spl::token_2022::MintTo {
            mint: ctx.accounts.dream_mint.to_account_info(),
            to: ctx.accounts.dreamer_dream_ata.to_account_info(),
            authority: ctx.accounts.treasury.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        let cpi_ctx = CpiContext::new_with_signer(cpi_program, cpi_accounts, signer);

        anchor_spl::token_2022::mint_to(cpi_ctx, reward_amount)?;

        emit!(DreamValidated {
            dreamer: dream_record.dreamer,
            ipfs_hash: dream_record.ipfs_hash.clone(),
            validation_score,
            reward_amount,
        });

        Ok(())
    }

    /// Claim SOL rebate from MEV protection
    pub fn claim_sol_rebate(
        ctx: Context<ClaimSolRebate>,
        backrun_profit: u64,
    ) -> Result<()> {
        let treasury = &mut ctx.accounts.treasury;
        
        // Calculate SOL rebate (1% of backrun profit, minimum 0.001 SOL)
        let rebate_amount = std::cmp::max(backrun_profit / 100, 1_000_000); // 0.001 SOL minimum
        
        require!(
            ctx.accounts.treasury.to_account_info().lamports() >= rebate_amount,
            ErrorCode::InsufficientTreasuryFunds
        );

        // Transfer SOL rebate to user
        **ctx.accounts.treasury.to_account_info().try_borrow_mut_lamports()? -= rebate_amount;
        **ctx.accounts.user.to_account_info().try_borrow_mut_lamports()? += rebate_amount;

        treasury.total_sol_rebates += rebate_amount;

        emit!(SolRebateClaimed {
            user: ctx.accounts.user.key(),
            rebate_amount,
            backrun_profit,
        });

        Ok(())
    }

    /// Stake SMIND tokens for governance
    pub fn stake_smind(
        ctx: Context<StakeSmind>,
        amount: u64,
    ) -> Result<()> {
        require!(amount > 0, ErrorCode::InvalidStakeAmount);

        let stake_account = &mut ctx.accounts.stake_account;
        
        if stake_account.amount == 0 {
            stake_account.staker = ctx.accounts.staker.key();
            stake_account.start_timestamp = Clock::get()?.unix_timestamp;
        }
        
        stake_account.amount += amount;
        stake_account.last_claim_timestamp = Clock::get()?.unix_timestamp;

        // Transfer SMIND tokens to treasury
        let cpi_accounts = anchor_spl::token_2022::Transfer {
            from: ctx.accounts.staker_smind_ata.to_account_info(),
            to: ctx.accounts.treasury_smind_ata.to_account_info(),
            authority: ctx.accounts.staker.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts);

        anchor_spl::token_2022::transfer(cpi_ctx, amount)?;

        emit!(SmindStaked {
            staker: ctx.accounts.staker.key(),
            amount,
            total_staked: stake_account.amount,
        });

        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + Treasury::LEN,
        seeds = [b"treasury"],
        bump
    )]
    pub treasury: Account<'info, Treasury>,
    
    #[account(mut)]
    pub authority: Signer<'info>,
    
    /// DREAM token mint (777,777,777 supply)
    pub dream_mint: InterfaceAccount<'info, MintInterface>,
    
    /// SMIND token mint (777,777,777 supply)
    pub smind_mint: InterfaceAccount<'info, MintInterface>,
    
    /// LUCID token mint (333,333,333 supply)
    pub lucid_mint: InterfaceAccount<'info, MintInterface>,
    
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
#[instruction(ipfs_hash: String)]
pub struct RecordDream<'info> {
    #[account(
        init,
        payer = dreamer,
        space = 8 + DreamRecord::LEN,
        seeds = [b"dream", dreamer.key().as_ref(), ipfs_hash.as_bytes()],
        bump
    )]
    pub dream_record: Account<'info, DreamRecord>,
    
    #[account(mut)]
    pub treasury: Account<'info, Treasury>,
    
    #[account(mut)]
    pub dreamer: Signer<'info>,
    
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct ValidateDream<'info> {
    #[account(mut)]
    pub dream_record: Account<'info, DreamRecord>,
    
    #[account(
        mut,
        seeds = [b"treasury"],
        bump = treasury.bump
    )]
    pub treasury: Account<'info, Treasury>,
    
    #[account(mut)]
    pub dream_mint: InterfaceAccount<'info, MintInterface>,
    
    #[account(
        mut,
        associated_token::mint = dream_mint,
        associated_token::authority = dream_record.dreamer,
        associated_token::token_program = token_program,
    )]
    pub dreamer_dream_ata: InterfaceAccount<'info, TokenAccountInterface>,
    
    pub validator: Signer<'info>,
    pub token_program: Program<'info, Token2022>,
    pub associated_token_program: Program<'info, AssociatedToken>,
}

#[derive(Accounts)]
pub struct ClaimSolRebate<'info> {
    #[account(
        mut,
        seeds = [b"treasury"],
        bump = treasury.bump
    )]
    pub treasury: Account<'info, Treasury>,
    
    #[account(mut)]
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct StakeSmind<'info> {
    #[account(
        init_if_needed,
        payer = staker,
        space = 8 + StakeAccount::LEN,
        seeds = [b"stake", staker.key().as_ref()],
        bump
    )]
    pub stake_account: Account<'info, StakeAccount>,
    
    #[account(
        mut,
        associated_token::mint = smind_mint,
        associated_token::authority = staker,
        associated_token::token_program = token_program,
    )]
    pub staker_smind_ata: InterfaceAccount<'info, TokenAccountInterface>,
    
    #[account(
        mut,
        associated_token::mint = smind_mint,
        associated_token::authority = treasury,
        associated_token::token_program = token_program,
    )]
    pub treasury_smind_ata: InterfaceAccount<'info, TokenAccountInterface>,
    
    #[account(
        seeds = [b"treasury"],
        bump = treasury.bump
    )]
    pub treasury: Account<'info, Treasury>,
    
    pub smind_mint: InterfaceAccount<'info, MintInterface>,
    
    #[account(mut)]
    pub staker: Signer<'info>,
    
    pub token_program: Program<'info, Token2022>,
    pub associated_token_program: Program<'info, AssociatedToken>,
    pub system_program: Program<'info, System>,
}

#[account]
pub struct Treasury {
    pub bump: u8,
    pub authority: Pubkey,
    pub dream_mint: Pubkey,
    pub smind_mint: Pubkey,
    pub lucid_mint: Pubkey,
    pub total_dreams: u64,
    pub total_sol_rebates: u64,
}

impl Treasury {
    pub const LEN: usize = 1 + 32 + 32 + 32 + 32 + 8 + 8;
}

#[account]
pub struct DreamRecord {
    pub dreamer: Pubkey,
    pub ipfs_hash: String,
    pub dream_content: String,
    pub timestamp: i64,
    pub validated: bool,
    pub validation_score: u8,
    pub reward_claimed: bool,
}

impl DreamRecord {
    pub const LEN: usize = 32 + 4 + 64 + 4 + 1000 + 8 + 1 + 1 + 1;
}

#[account]
pub struct StakeAccount {
    pub staker: Pubkey,
    pub amount: u64,
    pub start_timestamp: i64,
    pub last_claim_timestamp: i64,
}

impl StakeAccount {
    pub const LEN: usize = 32 + 8 + 8 + 8;
}

#[event]
pub struct TreasuryInitialized {
    pub authority: Pubkey,
    pub dream_mint: Pubkey,
    pub smind_mint: Pubkey,
    pub lucid_mint: Pubkey,
}

#[event]
pub struct DreamRecorded {
    pub dreamer: Pubkey,
    pub ipfs_hash: String,
    pub dream_content: String,
    pub timestamp: i64,
}

#[event]
pub struct DreamValidated {
    pub dreamer: Pubkey,
    pub ipfs_hash: String,
    pub validation_score: u8,
    pub reward_amount: u64,
}

#[event]
pub struct SolRebateClaimed {
    pub user: Pubkey,
    pub rebate_amount: u64,
    pub backrun_profit: u64,
}

#[event]
pub struct SmindStaked {
    pub staker: Pubkey,
    pub amount: u64,
    pub total_staked: u64,
}

#[error_code]
pub enum ErrorCode {
    #[msg("IPFS hash cannot be empty")]
    EmptyIpfsHash,
    #[msg("Dream content too long (max 1000 characters)")]
    DreamTooLong,
    #[msg("Invalid validation score (must be 0-100)")]
    InvalidValidationScore,
    #[msg("Dream already validated")]
    AlreadyValidated,
    #[msg("Insufficient treasury funds for rebate")]
    InsufficientTreasuryFunds,
    #[msg("Invalid stake amount")]
    InvalidStakeAmount,
}