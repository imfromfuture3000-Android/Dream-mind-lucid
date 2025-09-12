#!/usr/bin/env bash
# Setup GitHub repository secrets from a local .env file (or interactive prompts)
# Designed for use with Copilot Task Agent or local runs.
# Usage:
#   ./scripts/setup_github_secrets.sh [owner/repo] [path/to/.env]
# If no repo supplied, will use $GH_REPOSITORY or default to imfromfuture3000-Android/Dream-mind-lucid
set -euo pipefail

DEFAULT_REPO="imfromfuture3000-Android/Dream-mind-lucid"
REPO="${1:-${GH_REPOSITORY:-$DEFAULT_REPO}}"
ENV_FILE="${2:-.env}"
DRY_RUN=false

# Helper: print to stderr
err() { printf '%s\n' "$*" >&2; }

# Check dependencies
if ! command -v gh >/dev/null 2>&1; then
  err "Error: gh CLI is required. Install: https://cli.github.com/"
  exit 1
fi

# Ensure user is authenticated
if ! gh auth status >/dev/null 2>&1; then
  err "gh CLI not authenticated. Run: gh auth login (or set GH_TOKEN for non-interactive flows)"
  exit 1
fi

# Trim helper
trim() {
  local var="$*"
  var="${var#"${var%%[![:space:]]*}"}"
  var="${var%"${var##*[![:space:]]}"}"
  printf '%s' "$var"
}

declare -A kv

if [ -f "$ENV_FILE" ]; then
  echo "Loading $ENV_FILE ..."
  while IFS= read -r line || [ -n "$line" ]; do
    # Skip comments and blank lines
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "$line" ]] && continue
    if [[ "$line" =~ ^[[:space:]]*([A-Za-z0-9_]+)[[:space:]]*=(.*)$ ]]; then
      key="${BASH_REMATCH[1]}"
      val="${BASH_REMATCH[2]}"
      # trim whitespace first
      val="$(trim "$val")"
      # strip surrounding quotes
      val="${val%\"}"
      val="${val#\"}"
      val="${val%\'}"
      val="${val#\'}"
      kv["$key"]="$val"
    fi
  done < "$ENV_FILE"
else
  echo "No $ENV_FILE found; will prompt interactively."
fi

# Secrets list (aligned with Dream-Mind-Lucid workflows and ecosystem)
secrets=(
  # Core blockchain secrets
  INFURA_PROJECT_ID
  ALCHEMY_API_KEY
  ANKR_API_KEY
  DEPLOYER_KEY
  SOLANA_DEPLOYER_KEY
  WALLET_MNEMONIC
  ETHERSCAN_API_KEY
  
  # SKALE Network
  SKALE_RPC
  SKALE_CHAIN_ID
  
  # Solana Network
  SOLANA_RPC_URL
  
  # Gasless transaction relayers
  BICONOMY_API_KEY
  BICONOMY_FORWARDER_ADDRESS
  GELATO_API_KEY
  FORWARDER_ADDRESS
  
  # IPFS and decentralized storage
  IPFS_PROJECT_ID
  IPFS_PROJECT_SECRET
  
  # Frontend hosting platforms
  VERCEL_TOKEN
  VERCEL_ORG_ID
  VERCEL_PROJECT_ID
  NETLIFY_AUTH_TOKEN
  NETLIFY_SITE_ID
  FLEEK_API_KEY
  
  # AI and context APIs
  MODEL_CONTEXT_API_KEY
  MCP_API_KEY
)

echo "Target repo: $REPO"
echo "Setting up secrets for Dream-Mind-Lucid blockchain ecosystem..."
echo

for key in "${secrets[@]}"; do
  value="${kv[$key]:-}"
  if [ -z "$value" ]; then
    # Hidden input for sensitive names
    if [[ "$key" =~ (KEY|SECRET|MNEMONIC|DEPLOYER|MCP|TOKEN)$ ]]; then
      echo -n "Enter value for $key (hidden; ENTER to skip): "
      read -s input || true
      echo
    else
      read -p "Enter value for $key (ENTER to skip): " input || true
    fi
    value="$(trim "$input")"
  fi

  if [ -n "$value" ]; then
    if [ "$DRY_RUN" = true ]; then
      echo "[DRY RUN] would set secret $key"
    else
      printf '%s' "$value" | gh secret set "$key" -b - --repo "$REPO" && echo "✅ Set $key"
    fi
  else
    echo "⏭️  Skipping $key"
  fi
done

echo
echo "🎉 Done! Verify secrets at: https://github.com/$REPO/settings/secrets/actions"
echo "🌌 Your Dream-Mind-Lucid ecosystem is ready for zero-cost deployment! 🚀"