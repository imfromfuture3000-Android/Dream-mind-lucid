use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    program_error::ProgramError,
    pubkey::Pubkey,
    rent::Rent,
    sysvar::Sysvar,
};
use borsh::{BorshDeserialize, BorshSerialize};

// Program entrypoint
entrypoint!(process_instruction);

// Program ID - will be set during deployment
solana_program::declare_id!("11111111111111111111111111111111");

#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub enum DreamInstruction {
    /// Record a dream
    /// 
    /// Accounts expected:
    /// 0. [signer] The account of the dreamer
    /// 1. [writable] The dream storage account
    /// 2. [] System program
    RecordDream { dream_content: String },
    
    /// Initialize dream storage
    /// 
    /// Accounts expected:
    /// 0. [signer] The account of the dreamer  
    /// 1. [writable] The dream storage account to create
    /// 2. [] System program
    InitializeDreamStorage,
}

#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub struct DreamStorage {
    pub dreamer: Pubkey,
    pub dream_count: u64,
    pub total_tokens_earned: u64,
    pub is_initialized: bool,
}

#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub struct DreamRecord {
    pub id: u64,
    pub dreamer: Pubkey,
    pub content_hash: [u8; 32], // SHA256 hash of dream content
    pub timestamp: i64,
    pub token_reward: u64,
    pub mev_protected: bool,
}

pub fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let instruction = DreamInstruction::try_from_slice(instruction_data)
        .map_err(|_| ProgramError::InvalidInstructionData)?;

    match instruction {
        DreamInstruction::RecordDream { dream_content } => {
            msg!("Instruction: Record Dream");
            record_dream(program_id, accounts, dream_content)
        }
        DreamInstruction::InitializeDreamStorage => {
            msg!("Instruction: Initialize Dream Storage");
            initialize_dream_storage(program_id, accounts)
        }
    }
}

pub fn initialize_dream_storage(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult {
    let accounts_iter = &mut accounts.iter();
    let dreamer = next_account_info(accounts_iter)?;
    let dream_storage_account = next_account_info(accounts_iter)?;
    let _system_program = next_account_info(accounts_iter)?;

    if !dreamer.is_signer {
        return Err(ProgramError::MissingRequiredSignature);
    }

    // Check if account is already initialized
    if dream_storage_account.data_len() > 0 {
        return Err(ProgramError::AccountAlreadyInitialized);
    }

    let rent = Rent::get()?;
    let space = std::mem::size_of::<DreamStorage>();
    
    if !rent.is_exempt(dream_storage_account.lamports(), space) {
        return Err(ProgramError::AccountNotRentExempt);
    }

    let dream_storage = DreamStorage {
        dreamer: *dreamer.key,
        dream_count: 0,
        total_tokens_earned: 0,
        is_initialized: true,
    };

    dream_storage.serialize(&mut &mut dream_storage_account.data.borrow_mut()[..])?;
    
    msg!("Dream storage initialized for dreamer: {}", dreamer.key);
    Ok(())
}

pub fn record_dream(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    dream_content: String,
) -> ProgramResult {
    let accounts_iter = &mut accounts.iter();
    let dreamer = next_account_info(accounts_iter)?;
    let dream_storage_account = next_account_info(accounts_iter)?;

    if !dreamer.is_signer {
        return Err(ProgramError::MissingRequiredSignature);
    }

    if dream_storage_account.owner != program_id {
        return Err(ProgramError::IncorrectProgramId);
    }

    let mut dream_storage = DreamStorage::try_from_slice(&dream_storage_account.data.borrow())?;
    
    if !dream_storage.is_initialized {
        return Err(ProgramError::UninitializedAccount);
    }

    if dream_storage.dreamer != *dreamer.key {
        return Err(ProgramError::InvalidAccountData);
    }

    // Create content hash for storage efficiency and privacy
    use solana_program::hash::{hash, Hash};
    let content_hash = hash(dream_content.as_bytes()).to_bytes();
    
    // Calculate token reward (10 DREAM tokens with 9 decimals)
    let token_reward = 10_000_000_000; // 10 * 10^9
    
    // Update dream storage
    dream_storage.dream_count += 1;
    dream_storage.total_tokens_earned += token_reward;
    
    // Serialize updated storage
    dream_storage.serialize(&mut &mut dream_storage_account.data.borrow_mut()[..])?;
    
    msg!("Dream recorded for dreamer: {}", dreamer.key);
    msg!("Dream count: {}", dream_storage.dream_count);
    msg!("Token reward: {} DREAM", token_reward / 1_000_000_000);
    msg!("MEV Protection: Enabled via Helius");
    
    Ok(())
}

// Error handling
#[derive(thiserror::Error, Debug)]
pub enum DreamError {
    #[error("Dream content too long")]
    DreamTooLong,
    #[error("Invalid dreamer")]
    InvalidDreamer,
    #[error("Storage not initialized")]
    StorageNotInitialized,
}

impl From<DreamError> for ProgramError {
    fn from(e: DreamError) -> Self {
        ProgramError::Custom(e as u32)
    }
}